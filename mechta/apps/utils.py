from website.models import SitePage
from forum.models import *
from django.apps import apps
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.db.models import F
from django.utils import timezone
from django.conf import settings
import datetime
import os


class DataMixin:

    @staticmethod
    def get_list_apps():
        return [apps.get_app_config(app.split('.')[0]) for app in settings.INSTALLED_APPS
                if not app.startswith("django.")]

    def get_menu_items(self):
        host = 'http://127.0.0.1:8000/'
        apps_items = []
        for app in self.get_list_apps():
            if hasattr(app, 'menu_name'):
                apps_items.append((app.menu_name, host + app.label + '/'))
        pages = SitePage.objects.filter(use_in_menu=True)
        return [(page.title, page.get_absolute_url()) for page in pages] + apps_items

    def get_context_model_content(self, context_model, **kwargs):
        params = kwargs
        list_apps = self.get_list_apps()
        for app in list_apps:
            try:
                model = apps.get_model(app.label, model_name=context_model)
            except LookupError:
                continue
        else:
            if params:
                qw = model.objects
                if params.get('id') is not None:
                    qw = qw.filter(id=params['id'])
                if params.get('values') is not None:
                    qw = qw.values(*params['values'])
                if params.get('order_by') is not None:
                    qw = qw.order_by(*params['order_by'])
                return qw
            else:
                return model.objects.all()

    @staticmethod
    def get_last_messages():
        return Message.objects.\
            values('user_id__username',
                   'user_id__profile__land_plot__number',
                   'topic_id__title',
                   'topic_id__id',
                   'topic_id__section_id__id',
                   'pub_date').\
            order_by('-pub_date')[:3]

    @staticmethod
    def get_count_topics():
        return Topic.objects.count()

    @staticmethod
    def get_count_messages():
        return Message.objects.count()

    @staticmethod
    def get_count_messages_after_last_visit(user):
        last_visit = Profile.objects.filter(user=user).values('last_visit')
        return Message.objects.filter(pub_date__gt=last_visit).count()

    @staticmethod
    def get_count_users():
        time_delta = datetime.timedelta(minutes=5)
        now = timezone.now()
        return ForumSession.objects.filter(last_visit__gt=(now - time_delta)).count()


    @staticmethod
    def get_total_users():
        return User.objects.count()

    @staticmethod
    def setup_session(request, user):
        now = timezone.now()
        page_url = request.path
        try:
            forum_session = ForumSession.objects.get(session_key=request.session.session_key)
            if page_url not in forum_session.pages_dict:
                forum_session.pages_dict[page_url] = '1'
            else:
                num = int(forum_session.pages_dict[page_url]) + 1
                forum_session.pages_dict[page_url] = str(num)
            forum_session.last_visit = now
            forum_session.user_id = user
            forum_session.save()
        except ForumSession.DoesNotExist:
            request.session.set_expiry(3600)  # Задаю нужное мне время жизни сессии
            request.session.save()
            ForumSession.objects.create(session_key=Session.objects.get(pk=request.session.session_key),
                                        last_visit=now,
                                        user_id=user,
                                        expire_date=Session.objects.get(
                                            pk=request.session.session_key).expire_date,
                                        pages_dict={page_url: '1'})

            session = ForumSession.objects.get(session_key=request.session.session_key)
            session.save()



    @staticmethod
    def update_page_counter(request):
        page_url = request.path
        try:
            forum_pages_counter = ForumPagesCounter.objects.get(page_url=page_url)
            forum_pages_counter.visited = (F('visited') + 1)
            forum_pages_counter.save()
        except ForumPagesCounter.DoesNotExist:
            ForumPagesCounter.objects.create(page_url=page_url, visited=1)
            forum_pages_counter = ForumPagesCounter.objects.get(page_url=page_url)
            forum_pages_counter.save()


    @staticmethod
    def get_total_visited(request_path):
        qw = ForumPagesCounter.objects.filter(page_url=request_path).values('visited')
        return qw[0] if qw else {'visited': 0}


    def add_user_context(self, context, request=None, context_model=None, is_forum_page=False, **kwargs):


        context['menu_items'] = self.get_menu_items()
        context['last_messages'] = self.get_last_messages()

        if context_model is not None:
            context[context_model] = self.get_context_model_content(context_model, **kwargs)
        if is_forum_page:
            user = request.user
            context['topics_numbers'] = self.get_count_topics()
            context['messages_numbers'] = self.get_count_messages()
            context['count_users'] = self.get_count_users()
            context['total_users'] = self.get_total_users()
            context['total_visited'] = self.get_total_visited(request.path)
            if user is not None and user.is_authenticated:
                context['total_messages_after_last_visit'] = self.get_count_messages_after_last_visit(user)
                self.setup_session(request, user)
            self.update_page_counter(request)
        return context


def set_read_topic(user, topic_id):
    topic = Topic.objects.get(pk=topic_id)
    _, _ = ForumReadTopic.objects.update_or_create(user=user, topic=topic, defaults={'last_view': timezone.now()})


def delete_old_avatar_file(instance):

    old_avatar = Avatar.objects.filter(pk=instance.pk)[0]
    if old_avatar.image != instance.image and old_avatar.image_url:
        # old_avatar.image.delete(save=True)
        file_path = os.path.join(settings.MEDIA_ROOT, old_avatar.image_url)
        try:
            os.remove(file_path)
        except OSError as e:
            print("Error: %s : %s" % (file_path, e.strerror))