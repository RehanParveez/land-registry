from django.apps import AppConfig

class OwnershipConfig(AppConfig):
    name = 'ownership'
    
    def ready(self):
      import ownership.signals
