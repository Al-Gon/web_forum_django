from website.models import SitePage
from forum.models import *
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.apps import apps



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


    def add_user_context(self, context, context_model=None, is_forum_page=False, **kwargs):
        context['menu_items'] = self.get_menu_items()
        context['last_messages'] = self.get_last_messages()
        if context_model is not None:
            context[context_model] = self.get_context_model_content(context_model, **kwargs)
        if is_forum_page:
            context['topics_numbers'] = self.get_count_topics()
            context['messages_numbers'] = self.get_count_messages()
        return context






        # context = kwargs
        # cats = Category.objects.annotate(Count('women'))
        #
        # user_menu = menu.copy()
        # if not self.request.user.is_authenticated:
        #     user_menu.pop(1)
        #
        # context['menu'] = user_menu
        #
        # context['cats'] = cats
        # if 'cat_selected' not in context:
        #     context['cat_selected'] = 0
        # return context
