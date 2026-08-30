"""Native Hermes adapter for the Continuous Anti-Deception Supervisor.

This plugin does not trust Hermes' self-report as the source of truth. It taps
Hermes' native lifecycle/tool hooks so the supervisor sees the actual runtime
trajectory: attempted tool calls, tool arguments, actual tool results, session
context, subagent lifecycle, and final outputs.

Set INTENTGUARD_SUPERVISOR_URL to an HTTP service implementing:
  POST /event -> {"action":"allow"|"block"|"intervene", "message":"..."}

In CLI mode, intervention messages are injected into the same active Hermes
conversation with ctx.inject_message(), which interrupts a running turn just as
if the human typed a correction.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

SUPERVISOR_URL = os.getenv("INTENTGUARD_SUPERVISOR_URL", "http://127.0.0.1:8765")
TIMEOUT = float(os.getenv("INTENTGUARD_HOOK_TIMEOUT", "8"))


def _post(event: dict[str, Any]) -> dict[str, Any]:
    raw = json.dumps(event, default=str).encode("utf-8")
    req = urllib.request.Request(
        f"{SUPERVISOR_URL.rstrip('/')}/event",
        data=raw,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            body = response.read().decode("utf-8")
        value = json.loads(body or "{}")
        return value if isinstance(value, dict) else {}
    except Exception as exc:
        # Fail-open at the transport layer for the MVP. Production deployments
        # should make this policy configurable (fail-open vs fail-closed).
        return {"action": "allow", "observer_error": str(exc)}


def register(ctx):
    """Register the anti-deception observation plane using native Hermes hooks."""

    def emit(kind: str, **payload):
        return _post({"source": "hermes_runtime", "kind": kind, **payload})

    def pre_tool_call(tool_name: str, args: dict, task_id: str = "", **kwargs):
        decision = emit(
            "TOOL_CALL_REQUESTED",
            tool_name=tool_name,
            args=args,
            task_id=task_id,
            runtime=kwargs,
        )
        action = decision.get("action")
        message = decision.get("message") or "Blocked by anti-deception supervisor"
        if action == "block":
            return {"action": "block", "message": message}
        if action == "intervene" and message:
            ctx.inject_message(message, role="user")
            return {"action": "block", "message": "Paused for supervisor intervention"}
        return None

    def post_tool_call(
        tool_name: str,
        args: dict,
        result: str,
        task_id: str = "",
        duration_ms: int = 0,
        **kwargs,
    ):
        decision = emit(
            "TOOL_RESULT_OBSERVED",
            tool_name=tool_name,
            args=args,
            result=result,
            task_id=task_id,
            duration_ms=duration_ms,
            runtime=kwargs,
        )
        if decision.get("action") == "intervene" and decision.get("message"):
            ctx.inject_message(decision["message"], role="user")

    def pre_llm_call(
        session_id: str = "",
        user_message: str = "",
        conversation_history: list | None = None,
        is_first_turn: bool = False,
        model: str = "",
        platform: str = "",
        **kwargs,
    ):
        decision = emit(
            "LLM_TURN_START",
            session_id=session_id,
            user_message=user_message,
            conversation_history=conversation_history or [],
            is_first_turn=is_first_turn,
            model=model,
            platform=platform,
            runtime=kwargs,
        )
        context = decision.get("context")
        if context:
            return {"context": context}
        return None

    def post_llm_call(**kwargs):
        decision = emit("LLM_TURN_END", runtime=kwargs)
        if decision.get("action") == "intervene" and decision.get("message"):
            ctx.inject_message(decision["message"], role="user")

    def subagent_start(**kwargs):
        emit("SUBAGENT_START", runtime=kwargs)

    def subagent_stop(**kwargs):
        decision = emit("SUBAGENT_STOP", runtime=kwargs)
        if decision.get("action") == "intervene" and decision.get("message"):
            ctx.inject_message(decision["message"], role="user")

    def on_session_start(**kwargs):
        emit("SESSION_START", runtime=kwargs)

    def on_session_end(**kwargs):
        emit("SESSION_END", runtime=kwargs)

    ctx.register_hook("pre_tool_call", pre_tool_call)
    ctx.register_hook("post_tool_call", post_tool_call)
    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("post_llm_call", post_llm_call)
    ctx.register_hook("subagent_start", subagent_start)
    ctx.register_hook("subagent_stop", subagent_stop)
    ctx.register_hook("on_session_start", on_session_start)
    ctx.register_hook("on_session_end", on_session_end)
