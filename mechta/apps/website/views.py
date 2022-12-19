from django.views.generic import DetailView, ListView
from mechta.apps.utils import DataMixin
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
