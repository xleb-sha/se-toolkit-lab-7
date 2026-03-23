"""LLM client for intent-based natural language routing.

Provides tool calling interface: user message → LLM with tool definitions → API calls → response.
"""

import json
import sys
from typing import Any

import httpx


# Tool definitions for all 9 backend endpoints
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks from the LMS backend",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day timeline for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return, e.g. 5"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM to encourage tool use
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). You have access to tools that let you fetch data about labs, students, scores, and analytics.

When the user asks a question, use the available tools to fetch the relevant data. Then summarize the results in a clear, helpful way.

If the user asks about:
- Available labs → use get_items
- Scores or pass rates for a lab → use get_pass_rates with the lab identifier
- Top students → use get_top_learners
- Group performance → use get_groups
- Timeline of submissions → use get_timeline
- Completion rate → use get_completion_rate
- All students → use get_learners
- Refreshing data → use trigger_sync

For multi-step questions (e.g., "which lab has the lowest pass rate?"), you may need to:
1. First call get_items to get all labs
2. Then call get_pass_rates for each lab
3. Compare the results and provide an answer

If the user's message is a greeting (hello, hi, etc.), respond warmly and mention what you can help with.

If the user's message is unclear or seems like gibberish, politely ask for clarification and suggest what you can help with.

Always use tools to fetch real data before answering questions about the LMS. Do not make up data."""


class LLMClient:
    """Client for LLM API with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the LLM client.

        Args:
            api_key: API key for authentication.
            base_url: Base URL of the LLM API (e.g., http://localhost:42005/v1).
            model: Model name to use.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,  # Longer timeout for LLM responses
        )

    def chat_with_tools(
        self,
        user_message: str,
        tools: list[dict[str, Any]] | None = None,
        debug: bool = False,
    ) -> str:
        """Send a message to the LLM with tool definitions and handle tool calling loop.

        Args:
            user_message: The user's message.
            tools: List of tool definitions (uses TOOL_DEFINITIONS if None).
            debug: If True, print debug info to stderr.

        Returns:
            The LLM's final response.
        """
        if tools is None:
            tools = TOOL_DEFINITIONS

        # Initialize conversation with system prompt
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        # Tool calling loop - max iterations to prevent infinite loops
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call LLM
            response = self._client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                },
            )
            response.raise_for_status()
            result = response.json()

            # Get assistant message
            assistant_message = result["choices"][0]["message"]
            messages.append(assistant_message)

            # Check for tool calls
            tool_calls = assistant_message.get("tool_calls", [])

            if not tool_calls:
                # No tool calls - LLM is done, return the response
                return assistant_message.get("content", "No response")

            # Execute tool calls
            if debug:
                print(f"[tool] LLM called {len(tool_calls)} tool(s)", file=sys.stderr)

            for tool_call in tool_calls:
                function = tool_call["function"]
                tool_name = function["name"]
                tool_args = json.loads(function["arguments"]) if function["arguments"] else {}

                if debug:
                    print(f"[tool] {tool_name}({tool_args})", file=sys.stderr)

                # Execute the tool
                tool_result = self._execute_tool(tool_name, tool_args)

                if debug:
                    result_preview = str(tool_result)[:100] + "..." if len(str(tool_result)) > 100 else str(tool_result)
                    print(f"[tool] Result: {result_preview}", file=sys.stderr)

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(tool_result) if isinstance(tool_result, (dict, list)) else str(tool_result),
                })

            if debug:
                print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

        # Max iterations reached
        return "I'm having trouble processing this request. Please try rephrasing."

    def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by calling the appropriate backend endpoint.

        Args:
            name: Tool name (e.g., "get_items", "get_pass_rates").
            arguments: Tool arguments.

        Returns:
            Tool execution result.
        """
        # Import here to avoid circular imports
        from services.api_client import create_lms_client
        from config import load_config

        config = load_config()
        lms = create_lms_client(config["LMS_API_URL"], config["LMS_API_KEY"])

        try:
            if name == "get_items":
                return lms.get_items()
            elif name == "get_learners":
                return lms.get_learners()
            elif name == "get_scores":
                return lms.get_scores(arguments.get("lab", ""))
            elif name == "get_pass_rates":
                return lms.get_pass_rates(arguments.get("lab", ""))
            elif name == "get_timeline":
                return lms.get_timeline(arguments.get("lab", ""))
            elif name == "get_groups":
                return lms.get_groups(arguments.get("lab", ""))
            elif name == "get_top_learners":
                return lms.get_top_learners(arguments.get("lab", ""), arguments.get("limit", 5))
            elif name == "get_completion_rate":
                return lms.get_completion_rate(arguments.get("lab", ""))
            elif name == "trigger_sync":
                return lms.trigger_sync()
            else:
                return {"error": f"Unknown tool: {name}"}
        finally:
            lms.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "LLMClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


def create_llm_client(api_key: str, base_url: str, model: str) -> LLMClient:
    """Create an LLM client instance.

    Args:
        api_key: API key for authentication.
        base_url: Base URL of the LLM API.
        model: Model name to use.

    Returns:
        Configured LLMClient instance.
    """
    return LLMClient(api_key, base_url, model)
