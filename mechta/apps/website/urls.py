from django.urls import path
from . import views


app_name = 'website'
urlpatterns = [path('', views.HomePage.as_view(), name='home'),
               path('<slug:alias_slug>/', views.Page.as_view(), name='page')]