FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install --upgrade pip

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --prefix="/install" .

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "chatbot.adapters.api.main:app", "--host", "0.0.0.0", "--port", "8000"]