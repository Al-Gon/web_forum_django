from django.urls import path
from . import views
# from django.conf import settings
# from django.conf.urls.static import static


app_name = 'forum'
urlpatterns = [path('', views.ViewPage.as_view(), name='page'),
               # path('test/', views.test, name='test'),
               # path('test/test/', views.TestView.as_view(), name='test'),
               #path('profile/<slug:user_slug>/', views.TestUserProfile.as_view(), name='user_profile'),
               path('<int:section_id>/', views.ViewSection.as_view(), name='section'),
               path('<int:section_id>/create_topic', views.CreateTopic.as_view(), name='create_topic'),
               path('<int:section_id>/<int:topic_id>/', views.ViewTopic.as_view(), name='topic'),
               path('<int:section_id>/<int:topic_id>/reply/', views.CreateMessage.as_view(), name='reply'),
               path('unread_topics/', views.ViewUnreadTopics.as_view(), name='unread_topics'),
               path('members/', views.ViewMembers.as_view(), name='members'),
               path('search_results/', views.SearchResult.as_view(), name='search_results'),
               path('profile/<slug:user_slug>/', views.UserProfile.as_view(), name='user_profile'),


               path('profile/<slug:user_slug>/update/', views.UserProfileUpdate.as_view(), name='user_profile_update'),
               path('login/', views.LoginUser.as_view(), name='login'),
               path('logout/', views.logout_user, name='logout'),
               path('register/', views.RegisterUser.as_view(), name='register'),
               path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
                    views.ActivateUser.as_view(), name='activate'),
               path('password-reset/', views.PasswordReset.as_view(), name='password_reset'),
               path('password-reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
               path('password-reset-confirm/<uidb64>/<token>/',
                    views.PasswordResetConfirm.as_view(),
                    name='password_reset_confirm'),
               path('password-reset-complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
               path('topic-handler/', views.topic_handler, name='topic-handler'),
               ]

# # включаем возможность обработки картинок
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)