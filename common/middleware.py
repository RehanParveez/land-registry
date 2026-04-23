import uuid
import threading

_thread_locals = threading.local()
def get_current_trace_id():
  return getattr(_thread_locals, 'trace_id', None)

class DistributedTracingMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    trace_id = request.headers.get('X-Trace-ID', str(uuid.uuid4()))
    _thread_locals.trace_id = trace_id
        
    resp = self.get_response(request)
    resp['X-Trace-ID'] = trace_id
    if hasattr(_thread_locals, 'trace_id'):
      del _thread_locals.trace_id
            
    return resp