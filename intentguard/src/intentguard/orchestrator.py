from __future__ import annotations

from dataclasses import asdict, replace

from .audit import HashChainAuditLog
from .models import AgentEvent, CommitPolicy, IntentEnvelope, Verdict
from .policy import deterministic_verify
from .providers import Committer, Executor, IndependentVerifier


class IntentGuard:
    """Reference orchestration layer implementing verify-before-commit semantics."""

    def __init__(self, executor: Executor, committer: Committer, verifier: IndependentVerifier | None = None):
        self.executor = executor
        self.committer = committer
        self.verifier = verifier
        self.audit = HashChainAuditLog()

    def revise(self, intent: IntentEnvelope, **changes) -> IntentEnvelope:
        revised = replace(intent, revision=intent.revision + 1, **changes)
        self.audit.append({"event": "intent_revised", "intent": revised.canonical_payload(), "digest": revised.digest()})
        return revised

    def run(self, intent: IntentEnvelope, *, human_approved: bool = False) -> dict:
        self.audit.append({"event": "intent_received", "intent": intent.canonical_payload(), "digest": intent.digest()})

        events = self.executor.run(intent)
        for event in events:
            self.audit.append({"event": "agent_event", "data": asdict(event)})

        deterministic = deterministic_verify(intent, events)
        independent = self.verifier.verify(intent, events) if self.verifier else Verdict(passed=True)
        findings = deterministic.findings + independent.findings
        passed = deterministic.passed and independent.passed

        if intent.commit_policy == CommitPolicy.HUMAN_REQUIRED and not human_approved:
            passed = False
            block_reason = "human approval required"
        else:
            block_reason = None

        if not passed:
            result = {
                "status": "BLOCKED",
                "intent_digest": intent.digest(),
                "findings": [asdict(f) for f in findings],
                "reason": block_reason,
                "audit_head": self.audit.head,
            }
            self.audit.append({"event": "commit_blocked", "result": result})
            result["audit_head"] = self.audit.head
            return result

        receipt = self.committer.commit(intent, events)
        result = {
            "status": "COMMITTED",
            "intent_digest": intent.digest(),
            "receipt": receipt,
            "findings": [asdict(f) for f in findings],
            "audit_head": self.audit.head,
        }
        self.audit.append({"event": "commit_completed", "receipt": receipt})
        result["audit_head"] = self.audit.head
        return result
