from django.apps import AppConfig


class IshopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ishop'

    def ready(self):
        # add wor working with signals
        import ishop.signals
