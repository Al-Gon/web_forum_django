from django.apps import AppConfig


class ForumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forum'
    menu_name = 'Форум'

    def ready(self):
        from . import signals

