from django.apps import AppConfig

class ShardsConfig(AppConfig):
  name = 'shards'
    
  def ready(self):
    import shards.tasks
      
