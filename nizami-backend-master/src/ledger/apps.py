from django.apps import AppConfig


class LedgerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.ledger'
    
    def ready(self):
        # Import tasks to register scheduled tasks
        import src.ledger.tasks # noqa: F401