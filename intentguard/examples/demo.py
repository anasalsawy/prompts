from intentguard import AgentEvent, CommitPolicy, IntentEnvelope, IntentGuard, RiskClass


class DemoExecutor:
    def run(self, intent):
        return [
            AgentEvent(kind="tool_call", message="Read diagnostics", tool="read_logs"),
            AgentEvent(kind="tool_result", message="Service is healthy", tool="read_logs", evidence_id="ev-1"),
            AgentEvent(kind="claim", message="Diagnostics completed successfully", metadata={"evidence_refs": ["ev-1"]}),
        ]


class DemoCommitter:
    def commit(self, intent, events):
        return "demo://receipt/no-side-effect"


intent = IntentEnvelope(
    objective="Read service diagnostics and report health",
    allowed_tools=("read_logs",),
    forbidden_effects=("deploy", "delete"),
    risk=RiskClass.READ_ONLY,
    commit_policy=CommitPolicy.VERIFIED,
)

result = IntentGuard(DemoExecutor(), DemoCommitter()).run(intent)
print(result)
