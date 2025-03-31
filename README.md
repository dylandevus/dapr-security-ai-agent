# dapr-security-ai-agent

Security AI Agent built with dapr workflow

### DEVELOPMENT

Require:

*   `uv venv --python 3.13`
*   `uv init`
*   `pre-commit install`

Install:

```
$ uv venv
$ uv sync
$ uv run ruff format
$ uv run ruff check
```

Initialize DB:

```
Run: init.py
```

Run service:

```
Run: service.py
```

Run workflow:

```
$ dapr run --app-id dapr-agent-wf -- python workflow_main.py
```

Docker:

```
Build $ docker build -t dapr-agent:latest .
Run   $ docker run --env-file .env -p 127.0.0.1:8000:8000 dapr-agent:latest
```

### REFERENCES:

*   BIRD (BIg Bench for LaRge-scale Database Grounded Text-to-SQL Evaluation): https://bird-bench.github.io/
*   BIRD-CRITIC (a.k.a SWE-SQL), the first SQL diagnostic benchmark: https://bird-critic.github.io/
*   Spider 2.0 Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows: https://spider2-sql.github.io/