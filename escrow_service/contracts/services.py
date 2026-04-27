from django.core.exceptions import ValidationError

class ContractStateMachine:
  VALID_TRANSITIONS = {
    'draft': ['funded', 'cancelled'],
    'funded': ['verified', 'cancelled'],
    'verified': ['completed', 'cancelled'],
    'completed': [], 
    'cancelled': [], 
}

  @staticmethod
  def transition(agreement, new_status):
    curr_status = agreement.status
    if curr_status == new_status:
      return agreement
    allow_next_states = ContractStateMachine.VALID_TRANSITIONS.get(curr_status, [])
        
    if new_status not in allow_next_states:
      raise ValidationError(f'{curr_status} to {new_status}')
    agreement.status = new_status
    agreement.save()
    print(f'{agreement.id} moved to {new_status}')
        
    return agreement