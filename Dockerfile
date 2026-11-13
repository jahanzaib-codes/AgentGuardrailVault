# Multi-stage Dockerfile for AgentGuardrailVault
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim as runner

WORKDIR /app
RUN groupadd -r guardrail && useradd -r -g guardrail guardrail

COPY --from=builder /root/.local /home/guardrail/.local
COPY --chown=guardrail:guardrail . /app

ENV PATH=/home/guardrail/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER guardrail

ENTRYPOINT ["python", "cli.py"]
CMD ["demo"]
