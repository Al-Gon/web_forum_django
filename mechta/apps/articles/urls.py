from django.urls import path
from . import views


app_name = 'articles'

urlpatterns = [path('', views.ViewPage.as_view(), name='page'),
               path('<int:article_id>/', views.ArticleView.as_view(), name='article')]
