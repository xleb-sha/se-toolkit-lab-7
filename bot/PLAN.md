# Telegram Bot Development Plan

## Overview

This document outlines the development plan for building a Telegram bot that provides access to the LMS (Learning Management System) backend. The bot allows users to check system health, browse labs and scores, and ask questions in natural language using an LLM-powered intent router.

## Architecture

The bot follows a layered architecture with clear separation of concerns:

1. **Transport Layer** (`bot.py`) — Handles Telegram API communication via aiogram
2. **Handler Layer** (`handlers/`) — Command logic as pure functions (testable without Telegram)
3. **Service Layer** (`services/`) — API client for LMS backend, LLM client for intent routing
4. **Configuration** (`config.py`) — Environment variable loading and validation

This separation allows the same handler functions to work in three contexts: `--test` CLI mode, unit tests, and the live Telegram bot.

## Task 1: Scaffold and Testable Architecture

**Goal:** Create the project skeleton with `--test` mode for offline verification.

**Approach:**
- Create `bot/bot.py` as the entry point with `--test` flag support
- Implement placeholder handlers in `bot/handlers/commands.py`
- Each handler is a pure function: `handle_command(text: str) -> str`
- `--test` mode bypasses Telegram and calls handlers directly
- Configuration loaded from `.env.bot.secret` via `config.py`

**Key Decision:** Handlers don't import Telegram libraries. This makes them testable and reusable.

## Task 2: Backend Integration

**Goal:** Connect slash commands to the real LMS backend.

**Approach:**
- Create `services/api_client.py` with `LMSClient` class
- All API calls use Bearer token auth from `LMS_API_KEY`
- Implement 5 slash commands:
  - `/start` — Welcome message (no API call)
  - `/help` — Command list (no API call)
  - `/health` — `GET /items/` to verify backend is up
  - `/labs` — `GET /items/` filtered for lab items
  - `/scores <lab>` — `GET /analytics/pass-rates?lab=<lab_id>`
- Error handling: catch HTTP errors, show friendly messages with actual error details

**Key Decision:** API client is a separate class, not mixed into handlers. This makes it mockable for tests.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Allow users to ask questions in plain language.

**Approach:**
- Create `services/llm_client.py` with `LLMClient` class
- Define 9 tools matching backend endpoints (get_items, get_pass_rates, etc.)
- Tool descriptions must be specific enough for the LLM to choose correctly
- Implement tool calling loop:
  1. Send user message + tool definitions to LLM
  2. LLM returns tool calls
  3. Execute tools, collect results
  4. Feed results back to LLM
  5. LLM produces final answer
- Add inline keyboard buttons for common actions
- Fallback handling for greetings and gibberish

**Key Decision:** The LLM decides which tool to call — no regex or keyword matching in the routing path. If the LLM picks the wrong tool, fix the tool description, not the code.

## Task 4: Containerize and Document

**Goal:** Deploy the bot as a Docker service alongside the backend.

**Approach:**
- Create `bot/Dockerfile` using Python base image
- Install dependencies with `uv sync --frozen` (no pip, no requirements.txt)
- Add `bot` service to `docker-compose.yml`
- Configure Docker networking:
  - Backend URL: `http://backend:8000` (service name, not localhost)
  - LLM URL: `http://host.docker.internal:42005/v1` (via extra_hosts)
- Set restart policy: `unless-stopped`
- Update README with deployment instructions

**Key Decision:** Bot runs in Docker alongside backend, not as a background process. This ensures automatic restart and proper log management.

## Testing Strategy

- **Unit tests:** Test handlers in isolation (mock API client)
- **Integration tests:** Test `--test` mode with real backend
- **Manual testing:** Verify in Telegram after each task

## Deployment Checklist

1. Backend running and healthy (`curl http://localhost:42002/docs`)
2. `.env.bot.secret` exists with BOT_TOKEN, LMS_API_URL, LMS_API_KEY, LLM_API_KEY
3. Data synced (`curl http://localhost:42002/items/` returns items)
4. Bot container starts without errors
5. Bot responds in Telegram to `/start`

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| LLM OAuth token expires | Restart qwen-code-oai-proxy container |
| Backend returns empty data | Re-run ETL sync via POST /pipeline/sync |
| Docker networking issues | Use service names, not localhost |
| Handler crashes in Telegram but works in --test | Check bot.log for errors |
