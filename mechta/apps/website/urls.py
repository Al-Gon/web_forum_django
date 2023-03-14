# Core Django imports.
from django.urls import path

# Website application imports.
from . import views

# Specifies the app name for name spacing.
app_name = 'website'

# website/urls.py
urlpatterns = [

    # /
    path(
        route='',
        view=views.HomePage.as_view(),
        name='home'
    ),

    # /search_results/
    path(
        route='search_results/',
        view=views.SearchResult.as_view(),
        name='search_results'
    ),

    # /<alias_slug>/
    path(
        route='<slug:alias_slug>/',
        view=views.Page.as_view(),
        name='page'
    ),
]