# syntax=docker/dockerfile:1
# Una imagen por servicio Python del espacio de trabajo, desde el mismo Dockerfile:
#   docker build -f deploy/docker/Dockerfile --build-arg PACKAGE=ops-mcp       -t ops-mcp .
#   docker build -f deploy/docker/Dockerfile --build-arg PACKAGE=change-advisor -t change-advisor .
#   docker build -f deploy/docker/Dockerfile --build-arg PACKAGE=opsagent       -t ops-agent .
# El comando lo fija el manifiesto de Kubernetes (ops-mcp, change-advisor, opsagent-api).

ARG PYTHON_IMAGE=python:3.12.13-slim-trixie

FROM ghcr.io/astral-sh/uv:0.13.0 AS uv

FROM ${PYTHON_IMAGE} AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /src
COPY . .
ARG PACKAGE
# --frozen: exactamente lo de uv.lock; --no-editable: el código queda dentro del venv.
RUN uv sync --frozen --no-dev --no-editable --package "${PACKAGE}"

FROM ${PYTHON_IMAGE}
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
COPY --from=build /app/.venv /app/.venv
ENV PATH=/app/.venv/bin:$PATH PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER 10001
WORKDIR /app
