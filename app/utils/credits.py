from typing import Optional

def get_action_credit_cost(plan_type: Optional[str], action: str) -> int:
    """
    Returns the credit cost for various user actions based on their subscription plan.
    - Platinum: All features are 0 credits (Unlimited).
    - Gold:
      - contact_view: 3 credits
      - call: 1 credit / minute
      - send_interest: 1 credit
      - send_message: 1 credit
    - Silver:
      - contact_view: 4 credits
      - call: 2 credits / minute
      - send_interest: 1 credit
      - send_message: 1 credit
    - Free (None):
      - contact_view: 5 credits
      - call: 3 credits / minute
      - send_interest: 2 credits
      - send_message: 1 credit
    """
    plan = (plan_type or "").lower()
    
    if plan == "platinum":
        return 0
        
    if action == "contact_view":
        if plan == "gold":
            return 3
        elif plan == "silver":
            return 4
        else: # Free
            return 5
            
    elif action == "call":
        if plan == "gold":
            return 1
        elif plan == "silver":
            return 2
        else: # Free
            return 3
            
    elif action == "send_interest":
        if plan == "gold":
            return 1
        elif plan == "silver":
            return 1
        else: # Free
            return 2
            
    elif action == "send_message":
        if plan == "gold":
            return 1
        elif plan == "silver":
            return 1
        else: # Free
            return 1
            
    return 0
