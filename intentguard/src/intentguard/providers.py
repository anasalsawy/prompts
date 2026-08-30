from __future__ import annotations

from typing import Protocol
from .models import AgentEvent, IntentEnvelope, Verdict


class IntentCompiler(Protocol):
    def compile(self, user_input: str, source: str = "voice") -> IntentEnvelope: ...


class Executor(Protocol):
    def run(self, intent: IntentEnvelope) -> list[AgentEvent]: ...


class IndependentVerifier(Protocol):
    def verify(self, intent: IntentEnvelope, events: list[AgentEvent]) -> Verdict: ...


class Committer(Protocol):
    def commit(self, intent: IntentEnvelope, events: list[AgentEvent]) -> str: ...
