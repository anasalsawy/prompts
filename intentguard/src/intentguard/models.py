from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from hashlib import sha256
import json
import time
import uuid


class RiskClass(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE_WRITE = "reversible_write"
    HIGH_IMPACT = "high_impact"


class CommitPolicy(str, Enum):
    VERIFIED = "verified"
    HUMAN_OR_VERIFIED = "human_or_verified"
    HUMAN_REQUIRED = "human_required"


@dataclass(frozen=True)
class IntentEnvelope:
    objective: str
    constraints: tuple[str, ...] = ()
    allowed_tools: tuple[str, ...] = ()
    forbidden_effects: tuple[str, ...] = ()
    evidence_required: bool = True
    risk: RiskClass = RiskClass.READ_ONLY
    commit_policy: CommitPolicy = CommitPolicy.VERIFIED
    source: str = "voice"
    revision: int = 1
    intent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)

    def canonical_payload(self) -> dict:
        data = asdict(self)
        data["risk"] = self.risk.value
        data["commit_policy"] = self.commit_policy.value
        return data

    def digest(self) -> str:
        raw = json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"))
        return sha256(raw.encode()).hexdigest()


@dataclass(frozen=True)
class AgentEvent:
    kind: str
    message: str
    tool: str | None = None
    evidence_id: str | None = None
    side_effect: str | None = None
    metadata: dict = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    blocking: bool = True


@dataclass(frozen=True)
class Verdict:
    passed: bool
    findings: tuple[Finding, ...] = ()
