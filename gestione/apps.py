from django.apps import AppConfig

class GestioneConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestione'

    def ready(self):
        import gestione.signals
