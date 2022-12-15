from django.urls import path
from . import views


app_name = 'forum'
urlpatterns = [path('', views.ViewPage.as_view(), name='page'),
               # path('test/', views.test, name='test'),
               # path('test/test/', views.TestView.as_view(), name='test'),
               path('<int:section_id>/', views.ViewSection.as_view(), name='section'),
               path('<int:section_id>/create_topic', views.CreateTopic.as_view(), name='create_topic'),
               path('<int:section_id>/<int:topic_id>/', views.ViewTopic.as_view(), name='topic'),
               path('<int:section_id>/<int:topic_id>/reply/', views.ReplyPost.as_view(), name='reply'),
               path('search_results/', views.SearchResult.as_view(), name='search_results'),
               path('login/', views.LoginUser.as_view(), name='login'),
               path('logout/', views.logout_user, name='logout'),
               path('register/', views.RegisterUser.as_view(), name='register'),
               ]