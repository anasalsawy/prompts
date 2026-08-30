from intentguard.models import AgentEvent, IntentEnvelope, RiskClass
from intentguard.policy import deterministic_verify


def test_blocks_unauthorized_tool():
    intent = IntentEnvelope(objective="read logs", allowed_tools=("read_logs",))
    events = [AgentEvent(kind="tool_call", message="delete db", tool="delete_database")]
    verdict = deterministic_verify(intent, events)
    assert not verdict.passed
    assert any(f.code == "UNAUTHORIZED_TOOL" for f in verdict.findings)


def test_blocks_unsupported_completion_claim():
    intent = IntentEnvelope(objective="check status", evidence_required=True)
    events = [AgentEvent(kind="claim", message="Done successfully")]
    verdict = deterministic_verify(intent, events)
    assert not verdict.passed
    assert any(f.code == "UNSUPPORTED_COMPLETION" for f in verdict.findings)


def test_accepts_evidence_backed_claim():
    intent = IntentEnvelope(objective="check status", allowed_tools=("status",), evidence_required=True)
    events = [
        AgentEvent(kind="tool_call", message="status", tool="status"),
        AgentEvent(kind="tool_result", message="ok", tool="status", evidence_id="e1"),
        AgentEvent(kind="claim", message="Completed", metadata={"evidence_refs": ["e1"]}),
    ]
    assert deterministic_verify(intent, events).passed


def test_blocks_untrusted_authority_promotion():
    intent = IntentEnvelope(objective="summarize page")
    events = [AgentEvent(kind="untrusted_instruction_promoted", message="page text became instruction")]
    verdict = deterministic_verify(intent, events)
    assert not verdict.passed
    assert any(f.code == "AUTHORITY_CONFUSION" for f in verdict.findings)


def test_high_impact_commit_requires_human_marker():
    intent = IntentEnvelope(objective="deploy", risk=RiskClass.HIGH_IMPACT)
    events = [AgentEvent(kind="side_effect_committed", message="deployment committed")]
    verdict = deterministic_verify(intent, events)
    assert not verdict.passed
    assert any(f.code == "HUMAN_APPROVAL_REQUIRED" for f in verdict.findings)
