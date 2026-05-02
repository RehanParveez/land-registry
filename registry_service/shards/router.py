import threading

_thread_locals = threading.local()

def set_current_shard(shard_name):
  setattr(_thread_locals, 'shard_name', shard_name)

def get_current_shard():
  return getattr(_thread_locals, 'shard_name', None)

def clear_current_shard():
  if hasattr(_thread_locals, 'shard_name'):
    delattr(_thread_locals, 'shard_name')

class LandShardRouter:
  central_apps = ['shards', 'admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles']

  def db_for_read(self, model, **hints):
    if model._meta.app_label in self.central_apps:
      return 'default'
    shard = get_current_shard()
    if shard:
      return shard
    return 'default'

  def db_for_write(self, model, **hints):
    if model._meta.app_label in self.central_apps:
      return 'default' 
    shard = get_current_shard()
    if shard:
      return shard
    return 'default'

  def allow_relation(self, obj1, obj2, **hints):
    return True

  def allow_migrate(self, db, app_label, model_name=None, **hints):
    if app_label in self.central_apps:
      return db == 'default'  
    return True