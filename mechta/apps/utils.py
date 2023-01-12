from website.models import SitePage
from forum.models import *
from django.conf import settings
from django.apps import apps
from forum.models import ForumSession
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
import datetime
from django.db.models import F
from django.utils import timezone



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
                qw = model.objects.filter(id=params['id']).values(*params['values'])
                if params.get('order_by') is not None:
                    qw = qw.order_by(*params['order_by'])
                return qw
            else:
                return model.objects.all()

    @staticmethod
    def get_last_messages():
        return Message.objects.\
            values('user_id__username',
                   'user_id__profile__land_plot',
                   'topic_id__title',
                   'topic_id__id',
                   'topic_id__section_id__id',
                   'pub_date').\
            order_by('-pub_date')

    @staticmethod
    def get_count_topics():
        return Topic.objects.count()

    @staticmethod
    def get_count_messages():
        return Message.objects.count()

    @staticmethod
    def get_count_users():
        time_delta = datetime.timedelta(minutes=5)
        now = timezone.now()
        return ForumSession.objects.filter(last_visit__gt=(now - time_delta)).count()

    @staticmethod
    def get_total_users():
        return User.objects.count()

    @staticmethod
    def get_total_visited(request_path):
        qw = ForumPagesCounter.objects.filter(page_url=request_path).values('visited')
        return qw[0] if qw else {'visited': 0}

    def add_user_context(self, context, context_model=None, is_forum_page=False, request_path=None, **kwargs):

        context['menu_items'] = self.get_menu_items()
        context['last_messages'] = self.get_last_messages()

        if context_model is not None:
            context[context_model] = self.get_context_model_content(context_model, **kwargs)
        if is_forum_page:
            context['topics_numbers'] = self.get_count_topics()
            context['messages_numbers'] = self.get_count_messages()
            context['count_users'] = self.get_count_users()
            context['total_users'] = self.get_total_users()
            if request_path is not None:
                context['total_visited'] = self.get_total_visited(request_path)
        return context


def setup_session(request):
    if request.path.count('forum/'):
        page_url = request.path

        if request.user.is_authenticated:
            now = timezone.now()
            user_id = request.user.id
            user = User.objects.get(pk=user_id)
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
                                            expire_date=Session.objects.get(pk=request.session.session_key).expire_date,
                                            pages_dict={page_url: '1'})


                session = ForumSession.objects.get(session_key=request.session.session_key)
                session.save()

        try:
            forum_pages_counter = ForumPagesCounter.objects.get(page_url=page_url)
            forum_pages_counter.visited = (F('visited') + 1)
            forum_pages_counter.save()
        except ForumPagesCounter.DoesNotExist:
            ForumPagesCounter.objects.create(page_url=page_url, visited=1)
            forum_pages_counter = ForumPagesCounter.objects.get(page_url=page_url)
            forum_pages_counter.save()


def unpack_value(value_):
    def get_item(item_):
        item_ = item_.split('-')
        items_ = list(range(int(item_[0]), int(item_[1]) + 1))
        return list(map(lambda x: str(x), items_))

    value = value_.decode()
    items, result = [], []
    if value:
        items = value.split(',')

    for item in items:
        if '-' in item:
            result += get_item(item)
        else:
            result.append(item)
    return result

def pack_values(items):
    def get_item(tmp_list):
        return tmp_list[0] + '-' + tmp_list[-1] if len(tmp_list) > 1 else tmp_list[0]

    if items:
        items.sort(key=lambda x: int(x))
        result, tmp = [], []
        for item in items:
            if tmp:
                if int(item) - int(tmp[-1]) != 1:
                    result.append(get_item(tmp))
                    tmp.clear()
            tmp.append(item)
        result.append(get_item(tmp))
        result = ','.join(result)
    else:
        result = ''
    return bytes(result, encoding='utf-8')