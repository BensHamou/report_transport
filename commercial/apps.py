from django.apps import AppConfig


class CommercialConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "commercial"

    def ready(self):
        from .firebase_utils import init_firebase
        init_firebase()
