from django.apps import AppConfig

class ContractsConfig(AppConfig):
    name = 'contracts'
    
    def ready(self):
      import contracts.tasks
