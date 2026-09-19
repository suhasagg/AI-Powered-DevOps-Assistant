from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from starlette.responses import Response
from app.core.models import DevOpsRequest
from app.core.orchestrator import Orchestrator
app=FastAPI(title='AI-Powered DevOps Assistant',version='1.0.0')
runs=Counter('devops_assistant_runs_total','Orchestration runs')
@app.get('/health')
def health(): return {'status':'ok'}
@app.get('/metrics')
def metrics(): return Response(generate_latest(),media_type='text/plain')
@app.post('/v1/analyze')
async def analyze(req: DevOpsRequest): runs.inc(); return await Orchestrator().run(req)
