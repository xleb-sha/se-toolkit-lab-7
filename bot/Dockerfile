# Telegram bot Dockerfile
# Uses uv for dependency management (no pip, no requirements.txt)

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy bot dependencies
COPY bot/pyproject.toml bot/uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy bot source code
COPY bot/ ./bot/

# Set Python path to include bot directory
ENV PYTHONPATH=/app

# Run the bot
CMD ["uv", "run", "python", "-m", "bot.bot"]
