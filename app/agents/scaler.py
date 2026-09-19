from app.agents.base import BaseAgent
from app.core.models import *
class InfrastructureScaler(BaseAgent):
    name='infrastructure-scaler'
    async def run(self, req):
        cpu=float(req.context.get('cpu_percent',0)); replicas=int(req.context.get('replicas',1)); acts=[]
        if cpu>80:
            acts=[ProposedAction(action='scale_service',target=req.context.get('service','unknown'),parameters={'from':replicas,'to':min(replicas+2,20)},risk=Risk.medium,rationale=f'Sustained CPU supplied as {cpu}%.')]
        return AgentResult(agent=self.name,summary='Capacity signal assessment completed.',findings=[f'cpu={cpu}%, replicas={replicas}'],proposed_actions=acts,confidence=.78)
