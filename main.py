from fastapi import FastAPI, Request, HTTPException
from agent.reviewer import reviewer_graph
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title='AI Code Reviewer',
    description='Automatically reviews Pull Requests using LangGraph + Llama 3'
)

@app.get('/')
def health_check():
    return {'status': 'AI Code Reviewer is running'}

@app.post('/review')
async def review_pr(request: Request):
    body = await request.json()

    action = body.get('action')
    if action not in ['opened', 'synchronize']:
        return {'message': f'Skipping action: {action}'}

    repo_name = body['repository']['full_name']
    pr_number = body['pull_request']['number']

    print(f'Reviewing PR #{pr_number} in {repo_name}')

    initial_state = {
        'repo_name': repo_name,
        'pr_number': pr_number,
        'diff': '',
        'static_issues': '',
        'review': ''
    }

    reviewer_graph.invoke(initial_state)

    return {'message': f'Review posted for PR #{pr_number}'}