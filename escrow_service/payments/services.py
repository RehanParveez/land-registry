import time
import random

class MockBankingService:
  @staticmethod
  def process_external_payment():
    time.sleep(0.8) 
    if random.random() < 0.05:
      return {'status': 'failed', 'bank_ref': None}
    return {'status': 'success', 'bank_ref': f'BANK-{random.randint(100000, 999999)}'}