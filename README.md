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

Docker:

```
Build $ docker build -t dapr-agent:latest .
Run   $ docker run --env-file .env -p 127.0.0.1:8000:8000 dapr-agent:latest
```