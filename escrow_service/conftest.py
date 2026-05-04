import pytest
from contracts.models import Agreement
import uuid

@pytest.fixture
def sample_agreement(db):
  return Agreement.objects.create(parcel_id=uuid.uuid4(), buyer_uuid=uuid.uuid4(), seller_uuid=uuid.uuid4(),
    agreed_price=5000000.00, status = 'draft')