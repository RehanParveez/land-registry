import redis
import pybreaker

redis_client = redis.StrictRedis.from_url('redis://127.0.0.1:6379/2')

identity_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60,
  state_storage=pybreaker.CircuitRedisStorage(pybreaker.STATE_CLOSED, redis_client, namespace = 'circuit_identity'))

registry_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60,
  state_storage=pybreaker.CircuitRedisStorage(pybreaker.STATE_CLOSED, redis_client, namespace = 'circuit_registry'))

def breaker_call(breaker, func, *args, **kwargs):
  try:
    resp = breaker.call(func, *args, **kwargs)
    return resp, None
  except pybreaker.CircuitBreakerError:
    return None, 'the circuit is open. and depend serv is down.'
  except Exception as e:
    return None, f'network/service err: {str(e)}'