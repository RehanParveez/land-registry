import pytest
from topology.models import Province, Division, District, Tehsil, Mauza
from parcels.models import LandParcel
from decimal import Decimal
from ownership.services import TitleValidationService, OwnershipService
import uuid
from ownership.models import Title, Ledger
from unittest.mock import patch, MagicMock
import pytest
from rest_framework.test import APIClient
from legal.models import StayOrder, Charge
from datetime import date, timedelta

class RegistryBaseTest:
  @staticmethod
  def create_real_topology(using = 'default'):
    prov = Province.objects.using(using).create(name = 'Punjab', code = 'PJ02')
    div = Division.objects.using(using).create(name = 'LHR Div', code = 'LD02', province=prov)
    dist = District.objects.using(using).create(name = 'LHR Dist', code = 'LDT02', division=div)
    teh = Tehsil.objects.using(using).create(name = 'Raiwind', code = 'RW01', district=dist)
    mauza = Mauza.objects.using(using).create(name = 'Khayaban', code = 'KB01', tehsil=teh)
    return mauza

@pytest.mark.django_db(databases=['default', 'punjab', 'sindh'])
class TestOwnershipService(RegistryBaseTest):
    
  @pytest.fixture
  def sample_parcel(self):
    mauza = self.create_real_topology()  
    return LandParcel.objects.using('default').create(mauza=mauza, khasra_number = 'PB-LHR-025',
      square_footage=Decimal('1000.00'), land_use = 'residential', status = 'available')

  def test_validate_shares_success(self, sample_parcel):
    is_valid, message = TitleValidationService.validate_shares(parcel_id=sample_parcel.id, new_share=50.5, shard = 'default')
    assert is_valid is True
    assert message == 'Success'

  def test_validate_shares_exceeds_limit(self, sample_parcel):
    check_owner_id = str(uuid.uuid4())
    Title.objects.using('default').create(parcel=sample_parcel, owner_uuid = check_owner_id, share_perc=90)
    is_valid, message = TitleValidationService.validate_shares(parcel_id=sample_parcel.id, new_share=15, shard = 'default')
    assert is_valid is False
    assert 'exceeds 100% limit' in message

  def test_execute_transfer_new_owner(self, sample_parcel):
    share_to_transfer = Decimal('25.00')
    from_uuid = str(uuid.uuid4())
    to_uuid = str(uuid.uuid4())
    txn_ref = 'TXN-023'
    OwnershipService.execute_transfer(parcel=sample_parcel, from_uuid=from_uuid, to_uuid=to_uuid, share=share_to_transfer, price=500000,
      ref=txn_ref, shard = 'default')
    title = Title.objects.using('default').get(parcel=sample_parcel, owner_uuid=to_uuid)
    assert title.share_perc == share_to_transfer
    ledger = Ledger.objects.using('default').get(transaction_ref=txn_ref)
    assert str(ledger.from_owner_uuid) == from_uuid
    assert ledger.price == 500000

  def test_execute_transfer_existing_owner(self, sample_parcel):
    to_uuid = str(uuid.uuid4())
    seller_uuid = str(uuid.uuid4())
    Title.objects.using('default').create(parcel=sample_parcel, owner_uuid=to_uuid, share_perc=Decimal('10.00'))
    OwnershipService.execute_transfer(parcel=sample_parcel, from_uuid=seller_uuid, to_uuid=to_uuid, share=Decimal('20.00'), price=100000, ref = 'TXN-INC-01', shard = 'default')
    title = Title.objects.using('default').get(parcel=sample_parcel, owner_uuid=to_uuid)
    assert title.share_perc == Decimal('30.00') 

  def test_transfer_respects_shard(self):
    shard_name = 'punjab'
    to_uuid = str(uuid.uuid4())
    seller_uuid = str(uuid.uuid4())
    mauza_pj = RegistryBaseTest.create_real_topology(using=shard_name)
    parcel_pj = LandParcel.objects.using(shard_name).create(mauza=mauza_pj, khasra_number = 'PD-CHCEK-90', square_footage=Decimal('500.00'), land_use = 'agricultural')
    OwnershipService.execute_transfer(parcel=parcel_pj, from_uuid=seller_uuid, to_uuid=to_uuid, share=Decimal('10.00'),
      price=0, ref = 'SHARD-CHECK', shard=shard_name)
    assert Title.objects.using(shard_name).filter(owner_uuid=to_uuid).exists()
    assert not Title.objects.using('default').filter(owner_uuid=to_uuid).exists()

@pytest.mark.django_db 
class TestOwnershipSignals:
  @patch('redis.Redis')
  def test_ledger_post_save_emits_redis_event(self, mock_redis_class):
    mock_redis_client = MagicMock()
    mock_redis_class.return_value = mock_redis_client
    mauza = RegistryBaseTest.create_real_topology(using = 'default')
    sample_parcel = LandParcel.objects.using('default').create(mauza=mauza, khasra_number = 'CHECK-90', square_footage=Decimal('100.00'), land_use = 'residential')
    from_uid = str(uuid.uuid4())
    to_uid = str(uuid.uuid4())
    txn_ref = 'Check-023'
    price_val = Decimal('750000.00')
    Ledger.objects.using('default').create(parcel=sample_parcel, from_owner_uuid=from_uid, to_owner_uuid=to_uid, 
      transaction_ref=txn_ref, price=price_val)
    assert mock_redis_client.xadd.called
    args, kwargs = mock_redis_client.xadd.call_args
    stream_name = args[0]
    event_data = args[1]
    assert stream_name == 'title_transfers'
    assert event_data['ref'] == txn_ref
    assert event_data['from_owner'] == from_uid
    assert event_data['to_owner'] == to_uid
    assert event_data['price'] == str(price_val)
    assert event_data['parcel_id'] == str(sample_parcel.id)
    
@pytest.mark.django_db
class TestOwnershipViewSets:
  @pytest.fixture(autouse=True)
  def setup_base(self):
    self.client = APIClient()
    self.shard = 'default'
    self.base_url = f'/{self.shard}/ownership/title/'
    self.ledger_url = f'/{self.shard}/ownership/ledger/'
    self.mauza = RegistryBaseTest.create_real_topology(using=self.shard)
    self.valid_payload = {'share_perc': '100.00', 'owner_uuid': str(uuid.uuid4()), 'acquisition_type': 'purchase', 'price': '5000000.00'}

  def test_create_title_url_routing_and_success(self):
    parcel = LandParcel.objects.using(self.shard).create(mauza=self.mauza, khasra_number = 'URL-1', status = 'locked', square_footage=Decimal('1000.00'),
      land_use='residential')
    self.valid_payload["parcel"] = str(parcel.id)
    with patch('ownership.services.TitleValidationService.validate_shares', return_value=(True, "")):
      response = self.client.post(self.base_url, self.valid_payload)
      assert response.status_code == 201
      assert Title.objects.using(self.shard).count() == 1

  def test_create_title_fails_with_active_charge(self):
    parcel = LandParcel.objects.using(self.shard).create(mauza=self.mauza, khasra_number = 'BANK-1', status = 'locked', square_footage=Decimal('1000.00'),
      land_use = 'residential')
    Charge.objects.using(self.shard).create(parcel=parcel, bank_name = 'State Bank', loan_acc_num = 'LN-999', 
      loan_amount=Decimal('2500000.00'), is_active=True)
    self.valid_payload['parcel'] = str(parcel.id)
    response = self.client.post(self.base_url, self.valid_payload)
    assert response.status_code == 400
    assert 'active bank charge' in str(response.data)

  def test_create_title_fails_with_active_stay_order(self):
    parcel = LandParcel.objects.using(self.shard).create(mauza=self.mauza, khasra_number = 'COURT-1', status = 'locked', square_footage=Decimal('1000.00'),
      land_use='residential')
    StayOrder.objects.using(self.shard).create(parcel=parcel, court_name = 'High Court', case_num = 'HC-2026', issue_date=date.today(),
      expiry_date=date.today() + timedelta(days=30), is_active=True)
    self.valid_payload['parcel'] = str(parcel.id)
    response = self.client.post(self.base_url, self.valid_payload)
    assert response.status_code == 400
    assert 'active stay order' in str(response.data)

  def test_ledger_list_filtering(self):
    parcel = LandParcel.objects.using(self.shard).create(mauza=self.mauza, khasra_number = 'LEDG-1', square_footage=Decimal('1000.00'), land_use = 'residential')
    citizen_uuid = str(uuid.uuid4())
    Ledger.objects.using(self.shard).create(parcel=parcel, to_owner_uuid=citizen_uuid, transaction_ref='TX-REF', price=Decimal('5000000.00'))
    mock_auth = {'control': 'registrar', 'user_id': citizen_uuid}
    self.client.force_authenticate(user=None, token=mock_auth)
    response = self.client.get(f'{self.ledger_url}?parcel_id={parcel.id}')
    assert response.status_code == 200
    assert len(response.data) >= 1