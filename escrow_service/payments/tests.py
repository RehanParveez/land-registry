from django.test import TransactionTestCase
from unittest.mock import patch
from payments.services import MockBankingService
from contracts.models import Agreement
import uuid
from payments.models import Wallet, Payment
from rest_framework.test import APITestCase
from decimal import Decimal

class TestMockBankingService(TransactionTestCase):
  def test_process_external_payment_format(self):
    result = MockBankingService.process_external_payment()
    self.assertIn('status', result)
    self.assertIn('bank_ref', result)
    self.assertIn(result['status'], ['success', 'failed'])
    if result['status'] == 'success':
      self.assertTrue(result['bank_ref'].startswith('BANK-'))
    else:
      self.assertIsNone(result['bank_ref'])

  @patch('random.random')
  def test_process_payment_forced_failure(self, mock_random):
    mock_random.return_value = 0.02 
    result = MockBankingService.process_external_payment()
    self.assertEqual(result['status'], 'failed')
    self.assertIsNone(result['bank_ref'])

  @patch('random.random')
  @patch('random.randint')
  def test_process_payment_forced_success(self, mock_randint, mock_random):
    mock_random.return_value = 0.1 
    mock_randint.return_value = 123456
    result = MockBankingService.process_external_payment()
    self.assertEqual(result['status'], 'success')
    self.assertEqual(result['bank_ref'], 'BANK-123456')
    
class TestPaymentSignals(TransactionTestCase):
  def setUp(self):
    self.agreement = Agreement.objects.create(parcel_id=uuid.uuid4(), buyer_uuid=uuid.uuid4(), seller_uuid=uuid.uuid4(),
      agreed_price=5000.00, status = 'draft')

  def test_wallet_created_on_agreement_save(self):
    self.assertTrue(Wallet.objects.filter(agreement=self.agreement).exists())
    wallet = self.agreement.wallet
    self.assertEqual(wallet.balance, 0.00)

  @patch('payments.tasks.payment_notifi.delay')
  def test_payment_email_signal(self, mock_notifi):
    wallet = self.agreement.wallet
    Payment.objects.create(wallet=wallet, amount=5000.00, direction = 'in', status = 'pending')
    mock_notifi.assert_called_once_with(email = 'rehanrural@gmail.com', amount = '5000.00', status = 'pending')

  def test_on_payment_failure_signal(self):
    wallet = self.agreement.wallet
    Payment.objects.create(wallet=wallet, amount=5000.00, direction = 'in', status = 'failed')
    self.agreement.refresh_from_db()
    self.assertEqual(self.agreement.status, 'cancelled')

  def test_on_payment_success_no_transition(self):
    wallet = self.agreement.wallet
    Payment.objects.create(wallet=wallet, amount=5000.00, direction = 'in', status = 'success')
    self.agreement.refresh_from_db()
    self.assertEqual(self.agreement.status, 'draft')
    
class TestPaymentsViewSets(APITestCase):
  def setUp(self):
    self.buyer_id = str(uuid.uuid4())
    self.seller_id = str(uuid.uuid4())
    self.registrar_id = str(uuid.uuid4())
    self.agreement = Agreement.objects.create(parcel_id=uuid.uuid4(), buyer_uuid=self.buyer_id, seller_uuid=self.seller_id,
      agreed_price=Decimal('1000.00'), status = 'draft')
    self.wallet = self.agreement.wallet
    self.deposit_url = '/payments/wallet/deposit/'
    self.payments_url = '/payments/payment/'

  @patch('payments.services.MockBankingService.process_external_payment')
  def test_deposit_success_triggers_funded(self, mock_bank):
    mock_bank.return_value = {'status': 'success', 'bank_ref': 'BANK-323'}
    payload = {'user_id': self.buyer_id, 'control': 'citizen'}
    self.client.force_authenticate(user=None, token=payload)
    data = {'agreement_id': str(self.agreement.id), 'amount': '1000.00'}
    response = self.client.post(self.deposit_url, data)
    self.assertEqual(response.status_code, 200)
    self.wallet.refresh_from_db()
    self.agreement.refresh_from_db()
    self.assertEqual(self.wallet.balance, Decimal('1000.00'))
    self.assertEqual(self.agreement.status, 'funded')
    self.assertTrue(Payment.objects.filter(transaction_id = 'BANK-323').exists())

  @patch('payments.services.MockBankingService.process_external_payment')
  def test_deposit_failure_returns_400(self, mock_bank):
    mock_bank.return_value = {'status': 'failed', 'bank_ref': None}
    payload = {'user_id': self.buyer_id, 'control': 'citizen'}
    self.client.force_authenticate(user=None, token=payload)
    data = {'agreement_id': str(self.agreement.id), 'amount': '500.00'}
    response = self.client.post(self.deposit_url, data)
    self.assertEqual(response.status_code, 400)
    self.wallet.refresh_from_db()
    self.assertEqual(self.wallet.balance, Decimal('0.00'))

  def test_payment_visibility_citizen(self):
    Payment.objects.create(wallet=self.wallet, amount=100, direction = 'in', status = 'success')
    payload = {'user_id': self.buyer_id, 'control': 'citizen'}
    self.client.force_authenticate(user=None, token=payload)
    response = self.client.get(self.payments_url)
    self.assertEqual(len(response.data), 1)
    payload_other = {'user_id': str(uuid.uuid4()), 'control': 'citizen'}
    self.client.force_authenticate(user=None, token=payload_other)
    response_other = self.client.get(self.payments_url)
    self.assertEqual(len(response_other.data), 0)

  def test_payment_visibility_registrar(self):
    Payment.objects.create(wallet=self.wallet, amount=100, direction = 'in', status = 'success')
    payload = {'user_id': self.registrar_id, 'control': 'registrar'}
    self.client.force_authenticate(user=None, token=payload)
    response = self.client.get(self.payments_url)
    self.assertEqual(len(response.data), 1)