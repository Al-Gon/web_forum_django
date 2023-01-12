from django.urls import path
from . import views


app_name = 'articles'

urlpatterns = [path('', views.ViewPage.as_view(), name='page'),
               path('<slug:article_slug>/', views.ArticleView.as_view(), name='article')]
