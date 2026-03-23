#!/bin/bash
# Deploy script for Task 4 - Containerize and Deploy the Telegram bot
# Run this on the VM: ssh root@10.93.24.176 'bash -s' < deploy-bot.sh

set -e

echo "=== Task 4: Deploy Telegram Bot in Docker ==="

# Navigate to repo
cd ~/se-toolkit-lab-7

echo "[1/6] Pulling latest changes from GitHub..."
git pull

echo "[2/6] Checking .env.docker.secret..."
if [ ! -f .env.docker.secret ]; then
    echo "Creating .env.docker.secret from example..."
    cp .env.docker.example .env.docker.secret
    echo "WARNING: Please edit .env.docker.secret and set:"
    echo "  - BOT_TOKEN (from @BotFather)"
    echo "  - LMS_API_KEY (must match backend)"
    echo "  - LLM_API_KEY (must match qwen-code-api)"
    echo "  - QWEN_CODE_API_HOST_PORT=42005"
    echo ""
    echo "Then run: nano .env.docker.secret"
    exit 1
fi

# Verify required env vars
echo "[3/6] Verifying environment variables..."
source .env.docker.secret 2>/dev/null || true

missing_vars=()
if [ -z "$BOT_TOKEN" ] || [[ "$BOT_TOKEN" == "your-telegram-bot-token-here" ]]; then
    missing_vars+=("BOT_TOKEN")
fi
if [ -z "$LLM_API_KEY" ] || [[ "$LLM_API_KEY" == "your-qwen-api-key-here" ]]; then
    missing_vars+=("LLM_API_KEY")
fi

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "ERROR: Missing or placeholder values for:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please edit .env.docker.secret and set these values."
    exit 1
fi

echo "Environment variables OK"

echo "[4/6] Stopping background bot process (if running)..."
pkill -f "bot.py" 2>/dev/null || true

echo "[5/6] Building and starting all services..."
docker compose --env-file .env.docker.secret up --build -d

echo "[6/6] Verifying deployment..."
echo ""
echo "=== Service Status ==="
docker compose --env-file .env.docker.secret ps

echo ""
echo "=== Bot Logs (last 20 lines) ==="
docker compose --env-file .env.docker.secret logs bot --tail 20

echo ""
echo "=== Backend Health Check ==="
if curl -sf http://localhost:42002/docs -o /dev/null; then
    echo "Backend: OK (HTTP 200)"
else
    echo "Backend: FAILED"
fi

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Test the bot in Telegram: /start, /health, 'what labs are available?'"
echo "2. Check bot logs: docker compose --env-file .env.docker.secret logs -f bot"
echo ""
