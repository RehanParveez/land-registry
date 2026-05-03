from rest_framework.test import APITestCase, APIClient
from parcels.models import LandParcel
import uuid
from ownership.models import Title
from legal.models import StayOrder, Charge
from unittest.mock import patch
from topology.models import Province, Division, District, Tehsil, Mauza

class TestLegalApp(APITestCase):
  databases = {'default', 'punjab', 'sindh'}
  def setUp(self):
    self.client = APIClient()
    prov = Province.objects.using('punjab').create(name = 'Punjab', code = 'PUN-01', database_alias = 'punjab')
    div = Division.objects.using('punjab').create(name = 'Lahore Division', code = 'LHR-DIV', province=prov)
    dist = District.objects.using('punjab').create(name = 'Lahore', code = 'LHR-DIST', division=div)
    teh = Tehsil.objects.using('punjab').create(name = 'Lahore City', code = 'LHR-TEH', district=dist)
    self.mauza_punjab = Mauza.objects.using('punjab').create(name = 'Model Town', code = 'MT-023', tehsil=teh)
    self.parcel_punjab = LandParcel.objects.using('punjab').create(mauza=self.mauza_punjab, khasra_number = 'PUN-101', square_footage=5000, land_use = 'residential',
      status = 'available')
    self.citizen_uuid = str(uuid.uuid4())
    Title.objects.using('punjab').create(parcel=self.parcel_punjab, owner_uuid=self.citizen_uuid, share_perc=100.00)
    self.registrar_token = {'control': 'registrar', 'user_id': str(uuid.uuid4())}
    self.citizen_token = {'control': 'citizen', 'user_id': self.citizen_uuid}

  def modify_request_user(self, user_uuid, auth_payload):
    return patch.multiple('rest_framework.request.Request', user_id=user_uuid, auth=auth_payload, create=True)

  def test_apply_stay_order_punjab_shard(self):
    url = '/punjab/legal/stayorder/apply_stay/'
    data = {'parcel': self.parcel_punjab.id, 'court_name': 'Lahore High Court', 'case_num': 'LHC-2026-X', 'issue_date': '2026-05-01',
      'expiry_date': '2026-10-01'}
    self.client.force_authenticate(user=None, token=self.registrar_token)
    response = self.client.post(url, data)
    self.assertEqual(response.status_code, 201)
    self.assertTrue(StayOrder.objects.using('punjab').filter(case_num = 'LHC-2026-X').exists())

  def test_citizen_visibility_logic(self):
    StayOrder.objects.using('punjab').create(parcel=self.parcel_punjab, court_name = 'LHC', case_num = 'VISIBLE-1', 
      issue_date = '2026-05-01', expiry_date = '2026-10-01')
    url = '/punjab/legal/stayorder/'
    self.client.force_authenticate(user=None, token=self.citizen_token)
    response = self.client.get(url) 
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]['case_num'], 'VISIBLE-1')

  def test_release_logic_with_multiple_locks(self):
    stay = StayOrder.objects.using('punjab').create(parcel=self.parcel_punjab, court_name = 'LHC', case_num = 'CASE-1', 
      issue_date = '2026-05-01', expiry_date = '2026-10-01')
    Charge.objects.using('punjab').create(parcel=self.parcel_punjab, bank_name = 'Global Bank', loan_acc_num = 'AC-99',
      loan_amount=100000)
    self.parcel_punjab.status = 'locked'
    self.parcel_punjab.save(using = 'punjab')
    url = f'/punjab/legal/stayorder/{stay.id}/release_stay/'
    self.client.force_authenticate(user=None, token=self.registrar_token)
    response = self.client.post(url)
    stay.refresh_from_db(using = 'punjab')
    self.parcel_punjab.refresh_from_db(using = 'punjab')
    self.assertEqual(response.status_code, 200)
    self.assertFalse(stay.is_active)
    self.assertEqual(self.parcel_punjab.status, 'locked')
    self.assertIn('land remains locked', response.data['message'])

  def test_release_charge_logic_clears_status(self):
    Charge.objects.using('punjab').filter(parcel=self.parcel_punjab).delete()
    StayOrder.objects.using('punjab').filter(parcel=self.parcel_punjab).delete()
    charge = Charge.objects.using('punjab').create(parcel=self.parcel_punjab, bank_name = 'Global Bank',
      loan_acc_num = 'AC-100', loan_amount=200000)
    self.parcel_punjab.status = 'locked'
    self.parcel_punjab.save(using = 'punjab')
    url = f'/punjab/legal/charge/{charge.id}/release_charge/'
    self.client.force_authenticate(user=None, token=self.registrar_token)
    response = self.client.post(url)
    self.parcel_punjab.refresh_from_db(using = 'punjab')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(self.parcel_punjab.status, 'available')
    self.assertIn('land is now available', response.data['message'])