from app.agents.base import BaseAgent
from app.core.models import *
class CICDMonitor(BaseAgent):
    name='cicd-monitor'
    async def run(self, req):
        status=req.context.get('pipeline_status','unknown')
        acts=[]
        if status=='failed': acts=[ProposedAction(action='inspect_pipeline_failure',target=req.repository or 'pipeline',risk=Risk.low,rationale='Pipeline reports failure.')]
        return AgentResult(agent=self.name,summary=f'Pipeline status: {status}',findings=[f'deployment={req.context.get("deployment_status","unknown")}'],proposed_actions=acts,confidence=.9)
