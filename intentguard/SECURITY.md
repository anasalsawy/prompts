# Security model

IntentGuard is a risk-reduction control plane, not a proof that an AI agent cannot deceive.

## Security invariants

1. No side effect is trusted solely because the model says it happened.
2. Completion claims requiring tools must reference evidence.
3. Tool authorization is deterministic and external to the model.
4. Untrusted content cannot grant itself authority.
5. High-impact effects require a commit decision separate from generation.
6. Human overrides are explicit revisions and remain auditable.
7. Verifier approval cannot override a deterministic policy failure.

## Recommended production controls

- run executor and verifier in separate processes/containers
- keep credentials outside model context
- issue short-lived capability-scoped tool tokens
- require idempotency keys for write tools
- stage filesystem/database changes where possible
- hash tool outputs and important artifacts
- redact secrets before sending evidence to verifier models
- rate-limit recursive repair attempts
- require manual approval for destructive, financial, credential, account, deployment, and security-sensitive actions

## Known limitations

LLM judges can share blind spots with executors. Speech transcription can alter meaning. A compromised tool can fabricate tool results. Hash chains provide tamper evidence only if the anchor is stored somewhere the compromised process cannot rewrite. Policy definitions can themselves be wrong.

Use defense in depth.
