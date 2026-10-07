# Market Research Agent — Competitor Analysis

A LangGraph + LangChain + Tavily + Streamlit competitive-intelligence demo.

## Architecture

```text
Streamlit UI
    |
    v
ORCHESTRATOR
identify top 3 competitors
    |
    +---- Send(A) ---> Lead Researcher A ---+
    +---- Send(B) ---> Lead Researcher B ---+--> FINANCIAL ANALYST
    +---- Send(C) ---> Lead Researcher C ---+
                                               |
                                               v
                                      HUMAN REVIEW / INTERRUPT
                                               |
                                      approve + edit state
                                               |
                                               v
                                           COPYWRITER
                                               |
                                               v
                                           final report
```

The graph uses a standard `TypedDict` state. `raw_research` uses `Annotated[list, operator.add]`, allowing parallel research branches to append concurrently.

## Current LangGraph memory API

Current Python LangGraph uses `InMemorySaver` as the in-memory checkpointer and `InMemoryStore` as the in-memory cross-thread store.

- `InMemorySaver`: short-term/thread checkpointing; required for human interrupt/resume.
- `InMemoryStore`: cross-thread application memory.
- Both are RAM-only and reset when the Streamlit process restarts.

## Setup — Windows + VS Code

### 1. Create and activate the virtual environment

PowerShell:

```powershell
cd market_research_agent
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env`.

OpenAI option:

```env
MODEL_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-5.5
```

OpenRouter option:

```env
MODEL_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=google/gemini-2.5-flash
```

Tavily:

```env
TAVILY_API_KEY=your_key
```

LangSmith:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=market-research-agent
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### 3. Run the UI

```powershell
streamlit run app.py
```

Open `http://localhost:8501`.

### 4. Demonstrate the human interrupt

1. Enter a company/product such as `Notion`.
2. Click **Start Research**.
3. The Orchestrator finds exactly three competitors.
4. Three Lead Researchers run as parallel LangGraph branches.
5. The Financial Analyst synthesizes the collected evidence.
6. The graph stops before `copywriter`.
7. Review/edit the structured JSON in Streamlit.
8. Add optional reviewer feedback.
9. Click **Approve & Generate Report**.
10. The checkpoint is updated and the graph resumes at Copywriter.
11. The final Markdown report is displayed and downloadable.

### 5. CLI smoke test

```powershell
python -m src.main "Notion"
```

This runs until the human-review checkpoint.

### 6. Tests

```powershell
pytest -q
```

## Reference documents

Place `.md` or `.txt` files in:

```text
data/reference_docs/
```

The Lead Researcher has a `search_reference_docs` tool for this local knowledge base.

## Project structure

```text
market_research_agent/
├── app.py
├── README.md
├── ARCHITECTURE.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/reference_docs/
├── src/
│   ├── state.py
│   ├── config.py
│   ├── model.py
│   ├── memory.py
│   ├── agent_factory.py
│   ├── tools.py
│   ├── agents.py
│   ├── graph.py
│   └── main.py
├── skills/
│   ├── orchestrator/skills.md
│   ├── lead_researcher/skills.md
│   ├── financial_analyst/skills.md
│   └── copywriter/skills.md
└── tests/
```

## Agent design

### Orchestrator
Plans the job and writes exactly three competitors to state.

### Lead Researcher
Three instances run in parallel. Each searches Tavily and the local reference documents for pricing, features, positioning and news.

### Financial Analyst
Runs after all research branches finish. It normalizes evidence into structured JSON.

### Human Review
The graph is compiled with `interrupt_before=["copywriter"]`. The Streamlit user can edit the checkpointed `structured_insights` before resuming.

### Copywriter
Uses only approved structured data to generate the final Markdown briefing.

## Agent factory

`src/agent_factory.py` provides the project-specific factory:

```python
create_project_agent(
    name=...,
    description=...,
    system_prompt=...,
    tools=...,
    skills=...,
    model=...,
)
```

The `skills` string is loaded from each agent's `skills.md` and injected into its system prompt. The function returns a standard LangChain agent Runnable/CompiledStateGraph.

## Why this architecture is recruiter-friendly

- Explicit orchestration rather than one giant prompt.
- Dynamic parallelism using LangGraph `Send`.
- Reducer-based shared state.
- Separate agent responsibilities.
- Human-in-the-loop before final communication.
- Checkpoint/resume semantics.
- Cross-thread memory store.
- LangSmith observability.
- Streamlit UI for a live demonstration.
- Local document retrieval plus current web search.

## Production extensions

Replace in-memory persistence with Postgres, add authentication, scheduled weekly execution, source freshness scoring, citations, PDF export, Slack/email delivery, and MCP integrations for enterprise sources such as CRM, ticketing, call intelligence, and internal knowledge bases.
