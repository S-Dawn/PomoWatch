FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

# System libraries needed by Tkinter and audio playback.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3-tk \
        tk \
        libportaudio2 \
        libasound2 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv from the official image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev

COPY main.py ./

ENV PATH="/app/.venv/bin:${PATH}"

CMD ["python", "main.py"]
