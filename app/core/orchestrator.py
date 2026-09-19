import asyncio
from app.agents.code_analyzer import CodeAnalyzer
from app.agents.cicd_monitor import CICDMonitor
from app.agents.scaler import InfrastructureScaler
from app.agents.incident import IncidentResolver
from app.core.policy import authorize

class Orchestrator:
    def __init__(self): self.agents=[CodeAnalyzer(),CICDMonitor(),InfrastructureScaler(),IncidentResolver()]
    async def run(self, req):
        results=await asyncio.gather(*(a.run(req) for a in self.agents))
        decisions=[]
        for r in results:
            for a in r.proposed_actions:
                ok,reason=authorize(a,req.environment); decisions.append({'agent':r.agent,'action':a.model_dump(),'auto_authorized':ok,'policy_reason':reason})
        return {'results':[r.model_dump() for r in results],'decisions':decisions}
