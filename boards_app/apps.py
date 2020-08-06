from django.apps import AppConfig

class BoardsAppConfig(AppConfig):
    name = 'boards_app'

    def ready(self):
        from . import signals