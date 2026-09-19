import os
from github import Github

def client(): return Github(os.environ['GITHUB_TOKEN'])
def workflow_runs(repo: str): return list(client().get_repo(repo).get_workflow_runs()[:10])
