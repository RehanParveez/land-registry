from contracts.models import Agreement
import requests
from payments.models import Wallet
from contracts.services import ContractStateMachine
from django.conf import settings
from common.circuit_utils import identity_breaker, registry_breaker, breaker_call

class TransferProcessOperator:
  REGISTRY_BASE = 'http://127.0.0.1:8001'
  IDENTITY_URL = 'http://127.0.0.1:8000/verification/verify/verify_biometric/'

  @classmethod
  def execute(cls, agreement_id, shard_name='punjab', auth_token=None):
    print(f'the sent token {auth_token}')
    headers = {'Authorization': auth_token, 'Internal-Service-Token': settings.INTERNAL_SERVICE_SECRET} if auth_token else {
      'Internal-Service-Token': settings.INTERNAL_SERVICE_SECRET} 
    agreement = Agreement.objects.get(id=agreement_id)
    parcel_uuid = str(agreement.parcel_id) 
    lock_url = f'{cls.REGISTRY_BASE}/{shard_name}/parcels/parcel/{parcel_uuid}/lock/'
    lock_res, err = breaker_call(registry_breaker, requests.patch, lock_url, headers=headers, timeout=5)
    if err:
      return cls.abort_process(agreement, shard_name, err, auth_token, status_code=503)
    if lock_res.status_code != 200:
      return cls.abort_process(agreement, shard_name, 'registry: lock failed', auth_token, status_code=400)

    bio_payload = {'hash': 'BIO_SCAN_SUCCESS_99'} 
    bio_res, err = breaker_call(identity_breaker, requests.post, cls.IDENTITY_URL, json=bio_payload, headers=headers, timeout=5)
    if err:
      return cls.abort_process(agreement, shard_name, err, auth_token, status_code=503)
    if bio_res.status_code != 200:
      return cls.abort_process(agreement, shard_name, 'identity: biometric match failed', auth_token, status_code=400)

    wallet = Wallet.objects.get(agreement=agreement)
    if wallet.balance < agreement.agreed_price:
      return cls.abort_process(agreement, shard_name, 'escrow: funds are less', auth_token)

    title_url = f'{cls.REGISTRY_BASE}/{shard_name}/ownership/title/'
    title_payload = {'parcel': str(agreement.parcel_id), 'owner_uuid': str(agreement.buyer_uuid), 'price': str(agreement.agreed_price), 'share_perc': '100.0', 'acquisition_type': 'purchase'}
    title_res, err = breaker_call(registry_breaker, requests.post, title_url, json=title_payload, headers=headers, timeout=10)
    if err:
      return cls.abort_process(agreement, shard_name, err, auth_token, status_code=503)
    if title_res.status_code not in [200, 201]:
      return cls.abort_process(agreement, shard_name, 'registry: the title transfer has failed', auth_token, status_code=400)
    ContractStateMachine.transition(agreement, 'verified')
    ContractStateMachine.transition(agreement, 'completed')
    return {'success': True, 'message': 'the ownership transf. is done'}

  @classmethod
  def abort_process(cls, agreement, shard_name, reason, auth_token, status_code=400):
    headers = {'Authorization': auth_token} if auth_token else {}
    unlock_url = f'{cls.REGISTRY_BASE}/{shard_name}/parcels/parcel/{agreement.parcel_id}/unlock/'
    requests.patch(unlock_url, headers=headers)
    ContractStateMachine.transition(agreement, 'cancelled')
    return {'success': False, 'err': reason, 'status': status_code}