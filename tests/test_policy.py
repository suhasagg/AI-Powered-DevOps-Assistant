from app.core.models import ProposedAction,Risk
from app.core.policy import authorize
def test_prod_scale_blocked():
 a=ProposedAction(action='scale_service',target='api',risk=Risk.medium,rationale='x')
 assert authorize(a,'prod')[0] is False
def test_low_risk_read_allowed():
 a=ProposedAction(action='inspect_pipeline_failure',target='ci',risk=Risk.low,rationale='x')
 assert authorize(a,'dev')[0] is True
