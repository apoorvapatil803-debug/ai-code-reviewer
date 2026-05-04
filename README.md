# AI Code Review Agent 🤖

An autonomous AI agent that automatically reviews Pull Requests using LangGraph and Llama 3. When a PR is opened, the agent reads the code diff, runs static analysis, generates an intelligent review, and posts it as a comment — all within 60 seconds, with zero manual intervention.

## Demo

<!-- Add your demo GIF here after recording it -->
![Demo](demo.gif)

## How It Works

The agent is built as a 4-node LangGraph pipeline:

```
PR Opened → GitHub Actions → FastAPI → LangGraph Agent → PR Comment
                                            │
                                    ┌───────▼────────┐
                                    │  Node 1        │
                                    │  Parse Diff    │
                                    │  (GitHub API)  │
                                    └───────┬────────┘
                                            │
                                    ┌───────▼────────┐
                                    │  Node 2        │
                                    │  Static        │
                                    │  Analysis      │
                                    │  (flake8)      │
                                    └───────┬────────┘
                                            │
                                    ┌───────▼────────┐
                                    │  Node 3        │
                                    │  LLM Review    │
                                    │  (Llama 3)     │
                                    └───────┬────────┘
                                            │
                                    ┌───────▼────────┐
                                    │  Node 4        │
                                    │  Post Comment  │
                                    │  (GitHub API)  │
                                    └────────────────┘
```

1. **Parse Diff** — connects to GitHub API, reads every changed file in the PR
2. **Static Analysis** — runs flake8 on new lines of code, catches PEP 8 violations and syntax issues
3. **LLM Review** — sends the diff + static analysis results to Llama 3 via Groq for an intelligent review
4. **Post Comment** — formats and posts the structured review as a PR comment

## Tech Stack

| Technology | Purpose |
|---|---|
| LangGraph | Multi-node agent framework |
| FastAPI | Web server to receive GitHub webhooks |
| Llama 3 (via Groq) | LLM for intelligent code review |
| PyGithub | GitHub API integration |
| flake8 | Static analysis / linting |
| GitHub Actions | CI/CD automation |
| Docker | Containerization |

## Features

- Automatically triggers on every PR open and update
- Runs static analysis before LLM to reduce noise
- Structured review with Summary, Issues, Suggestions, and Verdict
- Zero manual intervention — fully automated pipeline
- Dockerized for easy deployment anywhere
- Modular node architecture — easily extensible

## Setup

### Prerequisites
- Python 3.11+
- Groq API key (free at console.groq.com)
- GitHub Personal Access Token

### Local Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ai-code-reviewer.git
cd ai-code-reviewer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install langchain-groq

# Add your keys
cp .env.example .env
# Edit .env with your actual keys

# Run the server
uvicorn main:app --reload
```

### Docker Setup

```bash
docker build -t ai-code-reviewer .
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e GITHUB_TOKEN=your_token \
  ai-code-reviewer
```

### Add to Your Repo

1. Copy `.github/workflows/review.yml` to your repo
2. Add `GROQ_API_KEY` and `GH_TOKEN` to your repo secrets
3. Open a Pull Request — the review appears automatically

## Example Review Output

```
## AI Code Review 🤖

### Summary
This PR adds a user authentication function using SQLite.

### Issues
🔴 CRITICAL: Line 6 — SQL query is vulnerable to SQL injection.
User input is concatenated directly into the query string.
Use parameterized queries instead.

### Suggestions
- Add input validation before database operations
- Consider using an ORM like SQLAlchemy
- Add docstrings to all public functions

### Verdict
REQUEST CHANGES
```

## Architecture Decision: Why LangGraph?

A plain Python script would work for a simple prototype. LangGraph was chosen because:
- Each node is independently testable and replaceable
- State flows explicitly between nodes — no hidden dependencies  
- Supports conditional branching for future enhancements
- Production-ready retry and error handling per node

## Future Improvements

- [ ] Convert to GitHub App for one-click installation
- [ ] Add Redis queue for handling 1000+ concurrent PRs
- [ ] Support for JavaScript, Java, Go (currently Python-focused)
- [ ] Dashboard showing review history across repos
- [ ] Retry logic with exponential backoff for LLM failures

## License

MIT
