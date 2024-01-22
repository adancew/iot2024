import sys

from django.apps import AppConfig


class ClientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clients'

    def ready(self):
        if 'runserver' in sys.argv:
            from .services import run
            run()
