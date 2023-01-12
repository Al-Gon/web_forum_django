from django.urls import path
from . import views


app_name = 'website'
urlpatterns = [path('', views.HomePage.as_view(), name='home'),
               path('search_results/', views.SearchResult.as_view(), name='search_results'),
               path('<slug:alias_slug>/', views.Page.as_view(), name='page')]