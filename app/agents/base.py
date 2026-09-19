from app.core.models import AgentResult, DevOpsRequest
class BaseAgent:
    name='base'
    async def run(self, req: DevOpsRequest) -> AgentResult: raise NotImplementedError
