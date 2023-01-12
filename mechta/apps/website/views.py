from django.views.generic import DetailView, ListView
from django.contrib.contenttypes.models import ContentType
from mechta.apps.utils import DataMixin
from django.db.models import Q
from .models import *

class HomePage(DataMixin, ListView):
    model = SitePage
    context_object_name = 'page'
    template_name = 'home_content.html'

    def get_queryset(self):
        return self.model.objects.get(pk=1)

    def get_context_data(self, **kwargs):

        context_model = self.object_list.context_model
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model=context_model)
        return context


class Page(DataMixin, DetailView):

    model = SitePage
    context_object_name = 'page'
    slug_url_kwarg = 'alias_slug'
    template_name_field = 'template'


    def get_context_data(self, **kwargs):

        context_model = self.object.context_model
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        context_model=context_model)
        return context


class SearchResult(DataMixin, ListView):
    context_object_name = 'page'
    model = SitePage
    model_ = ContentType.objects.get(app_label='articles', model='article').model_class()
    template_name = 'website/search_results.html'
    count_qw_1 = 0

    def get_queryset(self):
        query = self.request.GET.get('w_q').strip()
        if query:
            qw_1 = self.model.objects. \
                filter(Q(title__icontains=query) |
                       Q(intro_text__icontains=query) |
                       Q(content__icontains=query)).\
                values('title', 'intro_text', 'content', 'slug')
            qw_2 = self.model_.objects. \
                filter(Q(title__icontains=query) |
                       Q(text__icontains=query)). \
                values('title', 'text', 'text', 'slug')

            self.count_qw_1 = len(qw_1)

            return qw_1.union(qw_2)
        else:
            return {}

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context)
        context['query'] = self.request.GET.get('w_q').strip()
        if context['query']:
            context['qw_1'] = self.count_qw_1
        return context