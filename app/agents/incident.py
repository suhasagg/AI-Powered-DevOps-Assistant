from app.agents.base import BaseAgent
from app.core.models import *
class IncidentResolver(BaseAgent):
    name='incident-resolver'
    async def run(self, req):
        err=req.context.get('error_rate',0); findings=[f'error_rate={err}',f'latency_p95_ms={req.context.get("latency_p95_ms","unknown")}']
        acts=[]
        if float(err)>0.05:
            acts=[ProposedAction(action='rollback_deployment',target=req.context.get('service','unknown'),risk=Risk.high,rationale='Elevated error rate; validate temporal correlation with latest release before rollback.')]
        return AgentResult(agent=self.name,summary='Incident triage hypothesis generated.',findings=findings,proposed_actions=acts,confidence=.74)
