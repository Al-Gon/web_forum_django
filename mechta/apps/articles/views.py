from django.views.generic import DetailView, ListView
from mechta.apps.utils import DataMixin
from .models import *


class ViewPage(DataMixin, ListView):
    model = Article
    context_object_name = 'page'
    template_name = 'articles/articles_content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        )
        return context

class ArticleView(DataMixin, DetailView):
    model = Article
    context_object_name = 'page'
    template_name = 'articles/article.html'
    slug_url_kwarg = 'article_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_user_context(context=context,
                                        )
        return context