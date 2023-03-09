# Core Django imports.
from django.urls import path

# Forum application imports.
from forum.views.content.items_views import (
    ViewPage,
    SectionView,
    TopicView,
)

from forum.views.content.create_item_views import (
    CreateTopicView,
    CreateMessage,
)

from forum.views.content.stuff_views import (
    topic_handler,
    UnreadTopicView,
    SearchResult,
    ViewMembers,
)

from forum.views.account.register_views import (
    RegisterUser,
    ActivationConfirm,
    ActivateUser,
    PasswordReset,
    PasswordResetDone,
    PasswordResetConfirm,
    PasswordResetComplete,
)

from forum.views.account.login_logout_views import (
    LoginUser,
    logout_user,
)

from forum.views.user_profile.user_profile_views import (
    UserProfile,
    UserProfileUpdate,
)

# from django.conf import settings
# from django.conf.urls.static import static

# Specifies the app name for name spacing.
app_name = 'forum'


# forum/urls.py
urlpatterns = [
    # Content

    # /
    path(
        route='',
        view=ViewPage.as_view(),
        name='page'
    ),

    # /section_id/
    path(
        route='<int:section_id>/',
        view=SectionView.as_view(),
        name='section'
    ),

    # /section_id/topic_id/
    path(
        route='<int:section_id>/<int:topic_id>/',
        view=TopicView.as_view(),
        name='topic'
    ),

    # /unread_topics/
    path(
        route='unread_topics/',
        view=UnreadTopicView.as_view(),
        name='unread_topics'
    ),

    # /topic-handler/   (for ajax-request)
    path(
        route='topic-handler/',
        view=topic_handler,
        name='topic-handler'
    ),

    # '/members/'
    path(
        route='members/',
        view=ViewMembers.as_view(),
        name='members'
    ),

    # /search_results/
    path(
        route='search_results/',
        view=SearchResult.as_view(),
        name='search_results'
    ),

    # /section_id/create_topic/
    path(
        route='<int:section_id>/create_topic/',
        view=CreateTopicView.as_view(),
        name='create_topic'
    ),

    # /section_id/topic_id/reply/'
    path(
        route='<int:section_id>/<int:topic_id>/reply/',
        view=CreateMessage.as_view(),
        name='reply'
    ),

    # Account

    # /register/
    path(
        route='register/',
        view=RegisterUser.as_view(),
        name='register'
    ),

    # /activate/uidb64/token/
    path(
        route='activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        view=ActivateUser.as_view(),
        name='activate'
    ),

    # /activation-confirm/user_slug/
    path(
        route='activation-confirm/<slug:user_slug>/',
        view=ActivationConfirm.as_view(),
        name='activation_confirm'
    ),

    # /password-reset/'
    path(
        route='password-reset/',
        view=PasswordReset.as_view(),
        name='password_reset'
    ),

    # /password-reset/done/
    path(
        route='password-reset/done/',
        view=PasswordResetDone.as_view(),
        name='password_reset_done'
    ),

    # /password-reset-confirm/<uidb64>/<token>/
    path(
        route='password-reset-confirm/<uidb64>/<token>/',
        view=PasswordResetConfirm.as_view(),
        name='password_reset_confirm'
    ),

    # /password-reset-complete/
    path(
        route='password-reset-complete/',
        view=PasswordResetComplete.as_view(),
        name='password_reset_complete'
    ),

    # /login/
    path(
        route='login/',
        view=LoginUser.as_view(),
        name='login'
    ),

    # /logout/
    path(
        route='logout/',
        view=logout_user,
        name='logout'
    ),

    # User Profile

    # profile/user_slug/
    path(
        route='profile/<slug:user_slug>/',
        view=UserProfile.as_view(),
        name='user_profile'
    ),

    # profile/user_slug/update/
    path(
        route='profile/<slug:user_slug>/update/',
        view=UserProfileUpdate.as_view(),
        name='user_profile_update'
    ),
]

# # включаем возможность обработки картинок
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)