FROM python:3.13-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.3.1

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi


FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system appgroup && adduser --system --ingroup appgroup --no-create-home appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder --chown=appuser:appgroup /usr/local/bin /usr/local/bin

COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log"]
