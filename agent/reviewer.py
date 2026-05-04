import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from github import Github
from dotenv import load_dotenv
import subprocess
import tempfile

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name='llama-3.3-70b-versatile',
    temperature=0.2
)

github_client = Github(GITHUB_TOKEN)

class ReviewState(TypedDict):
    repo_name: str
    pr_number: int
    diff: str
    static_issues: str
    review: str

def parse_diff(state: ReviewState) -> ReviewState:
    repo = github_client.get_repo(state['repo_name'])
    pr = repo.get_pull(state['pr_number'])
    
    diff_text = ''
    for file in pr.get_files():
        if file.patch:
            diff_text += f'\n--- {file.filename} ---\n'
            diff_text += file.patch
    
    state['diff'] = diff_text
    return state

def static_analysis(state: ReviewState) -> ReviewState:
    issues = []
    
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False
    ) as tmp:
        added_lines = []
        for line in state['diff'].split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                added_lines.append(line[1:])
        tmp.write('\n'.join(added_lines))
        tmp_path = tmp.name
    
    result = subprocess.run(
        ['flake8', '--max-line-length=100', tmp_path],
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        issues.append(result.stdout)
    
    state['static_issues'] = '\n'.join(issues) if issues else 'No static analysis issues found'
    return state

def llm_review(state: ReviewState) -> ReviewState:
    prompt = f'''You are a senior software engineer doing a code review.

Here is the code diff (changes made in this Pull Request):
{state['diff']}

Here are the static analysis results:
{state['static_issues']}

Please provide a structured code review with these sections:
1. SUMMARY: Brief summary of what this PR does
2. ISSUES: Any bugs, security issues, or problems found (be specific with line references)
3. SUGGESTIONS: Improvements for code quality, readability, or performance
4. VERDICT: APPROVE, REQUEST CHANGES, or COMMENT

Keep your review clear, specific, and helpful. Format it nicely with markdown.'''

    response = llm.invoke(prompt)
    state['review'] = response.content
    return state

def post_review(state: ReviewState) -> ReviewState:
    repo = github_client.get_repo(state['repo_name'])
    pr = repo.get_pull(state['pr_number'])
    
    comment = f'''## AI Code Review 🤖

{state['review']}

---
*This review was generated automatically by an AI Code Review Agent*'''
    
    pr.create_issue_comment(comment)
    return state

def build_graph():
    graph = StateGraph(ReviewState)
    
    graph.add_node('parse_diff', parse_diff)
    graph.add_node('static_analysis', static_analysis)
    graph.add_node('llm_review', llm_review)
    graph.add_node('post_review', post_review)
    
    graph.set_entry_point('parse_diff')
    graph.add_edge('parse_diff', 'static_analysis')
    graph.add_edge('static_analysis', 'llm_review')
    graph.add_edge('llm_review', 'post_review')
    graph.add_edge('post_review', END)
    
    return graph.compile()

reviewer_graph = build_graph()
