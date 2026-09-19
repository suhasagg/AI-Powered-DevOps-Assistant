from app.core.models import ProposedAction, Risk

PROD_MUTATIONS = {'scale_service','rollback_deployment','restart_workload','apply_infrastructure'}

def authorize(action: ProposedAction, environment: str) -> tuple[bool,str]:
    # LLMs propose; deterministic policy authorizes. Never let generated text bypass this boundary.
    if environment == 'prod' and action.action in PROD_MUTATIONS:
        return False, 'Production mutation requires explicit human/change-management approval.'
    if action.risk in {Risk.high, Risk.critical}:
        return False, 'High-risk action requires human approval.'
    return True, 'Allowed by demo policy.'
