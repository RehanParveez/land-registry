import time
import random

class BiometricService:
  @staticmethod
  def verify_hash(biometric_hash):
    time.sleep(1)
    if biometric_hash == 'INVALID_SCAN':
      return False
            
    return random.random() > 0.1