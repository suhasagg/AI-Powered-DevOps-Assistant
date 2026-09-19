import json, os, urllib.request
def handler(event, context):
    payload=json.dumps({'tenant_id':'lambda','objective':'Analyze operational event','environment':event.get('environment','dev'),'context':event}).encode()
    req=urllib.request.Request(os.environ['ASSISTANT_URL']+'/v1/analyze',data=payload,headers={'content-type':'application/json'})
    with urllib.request.urlopen(req,timeout=10) as r: return {'statusCode':200,'body':r.read().decode()}
