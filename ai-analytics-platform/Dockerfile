FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# system libs for pandas, matplotlib, postgres
RUN apt-get update && apt-get install -y \
  build-essential gcc libpq-dev curl git && \
  rm -rf /var/lib/apt/lists/*

# Poetry install
RUN pip install --no-cache-dir poetry==1.8.2

WORKDIR /app
COPY pyproject.toml poetry.lock* README.md /app/
RUN poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi --only main

COPY src/ /app/src/

# uvicorn hot reload off for prod
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
