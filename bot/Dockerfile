# Telegram bot Dockerfile
# Uses uv for dependency management (no pip, no requirements.txt)

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy bot source code (includes pyproject.toml, uv.lock)
COPY bot/ ./

# Export dependencies and install with pip
RUN uv export --no-dev --no-hashes -o requirements.txt && \
    uv pip install --system -r requirements.txt

# Set Python path
ENV PYTHONPATH=/app

# Run the bot
CMD ["python", "bot.py"]
