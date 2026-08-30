from __future__ import annotations

from .models import AgentEvent, Finding, IntentEnvelope, RiskClass, Verdict


COMPLETION_WORDS = ("done", "completed", "success", "finished", "fixed", "deployed", "sent")


def deterministic_verify(intent: IntentEnvelope, events: list[AgentEvent]) -> Verdict:
    findings: list[Finding] = []
    allowed = set(intent.allowed_tools)
    forbidden = set(intent.forbidden_effects)
    evidence_ids = {e.evidence_id for e in events if e.kind in {"tool_result", "artifact"} and e.evidence_id}

    for event in events:
        if event.kind == "tool_call" and event.tool and event.tool not in allowed:
            findings.append(Finding("UNAUTHORIZED_TOOL", f"Tool '{event.tool}' was not authorized."))

        if event.side_effect and event.side_effect in forbidden:
            findings.append(Finding("FORBIDDEN_EFFECT", f"Forbidden side effect proposed/executed: {event.side_effect}."))

        if event.kind == "claim" and any(word in event.message.lower() for word in COMPLETION_WORDS):
            cited = event.metadata.get("evidence_refs", [])
            if intent.evidence_required and not cited:
                findings.append(Finding("UNSUPPORTED_COMPLETION", "Completion claim has no evidence reference."))
            for ref in cited:
                if ref not in evidence_ids:
                    findings.append(Finding("MISSING_EVIDENCE", f"Claim references unknown evidence '{ref}'."))

        if event.kind == "untrusted_instruction_promoted":
            findings.append(Finding("AUTHORITY_CONFUSION", "Untrusted content was promoted into executable authority."))

        if intent.risk == RiskClass.HIGH_IMPACT and event.kind == "side_effect_committed":
            if not event.metadata.get("human_approved", False):
                findings.append(Finding("HUMAN_APPROVAL_REQUIRED", "High-impact side effect committed without human approval."))

    return Verdict(passed=not any(f.blocking for f in findings), findings=tuple(findings))
