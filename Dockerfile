FROM python:3.13.0-slim

ENV USER=uv-example-user \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash $USER

COPY --from=ghcr.io/astral-sh/uv:0.5.5 /uv /uvx /bin/

ENV APP_DIR=/home/$USER/app

WORKDIR $APP_DIR

COPY src $APP_DIR
COPY uv.lock pyproject.toml $APP_DIR

ENV PYTHONPATH=$APP_DIR

RUN uv sync --frozen --no-dev

RUN chown -R "$USER":"$USER" $APP_DIR
USER $USER

# CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--workers", "4"]
CMD ["fastapi", "run", "service.py", "--workers", "4"]
