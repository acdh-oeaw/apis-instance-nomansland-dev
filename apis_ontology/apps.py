from django.apps import AppConfig


class ApisOntologyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apis_ontology'
    
    def ready(self):
        # Import signal handlers
        from . import signals