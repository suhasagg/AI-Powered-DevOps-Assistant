from app.agents.base import BaseAgent
from app.core.models import *
class CodeAnalyzer(BaseAgent):
    name='code-analyzer'
    async def run(self, req):
        findings=[]
        for f in req.context.get('changed_files',[]):
            if f.endswith(('.pem','.key')): findings.append(f'Potential secret/key material: {f}')
            if 'Dockerfile' in f: findings.append('Review container base image, user, package pinning and SBOM.')
        if not findings: findings=['Run SAST, dependency, secret, IaC and container scans; correlate only actionable findings.']
        return AgentResult(agent=self.name,summary='Security-focused change review completed.',findings=findings,confidence=.82)
