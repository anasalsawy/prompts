# IntentGuard

**A deception-resistant, intent-preserving control plane for AI agents.**

IntentGuard implements a separation-of-powers architecture between a human-facing executive model and an execution agent such as Hermes. It automates the common "talk to one model → refine the prompt → copy/paste into another model → inspect the result → send corrections back" workflow while adding explicit controls against fabrication, prompt drift, false tool-success claims, unintended side effects, and irreversible actions.

> Important: no architecture can guarantee that an AI system is literally "undeceivable." IntentGuard is designed to *reduce* deception and deviation risk through independent verification, evidence requirements, deterministic policy checks, staged side effects, and human override.

## Core idea

```text
 Human voice ───────► Executive / Intent Compiler ─────┐
 Human typed input ────────────────────────────────────┼──► Intent Envelope
                                                     │
                                                     ▼
                                             Execution Agent
                                               (e.g. Hermes)
                                                     │
                                 events + tool evidence + output
                                                     ▼
                                           Independent Verifier
                                                     │
                              ┌──────────── PASS ─────┴──── FAIL ────────────┐
                              ▼                                              ▼
                         Commit Gate                                  Block / repair / ask
                              │
                              ▼
                       User-visible result
```

The human always retains a direct typed override lane. Typed overrides are recorded as authoritative intent revisions rather than silently merged into prior instructions.

## Why this is different

Single-agent self-critique asks the same reasoning process to detect its own mistakes. IntentGuard separates roles and state:

1. **Executive / Intent Compiler** converts messy speech into an explicit structured contract. It does not execute.
2. **Intent Envelope** freezes objective, constraints, allowed tools, forbidden effects, evidence requirements, and commit policy.
3. **Executor** receives only the envelope plus explicitly authorized context.
4. **Observer stream** records claims, tool calls, tool results, artifacts, and proposed side effects.
5. **Verifier** runs in a separate context and compares observed behavior with the frozen envelope.
6. **Commit Gate** refuses irreversible changes until deterministic checks and verification pass.
7. **Human override** can supersede any prior intent without requiring a verbal negotiation loop.

## Threats addressed

- fabricated tool success
- unsupported factual claims
- instruction drift
- accidental scope expansion
- prompt injection crossing from untrusted data into executable instructions
- side effects occurring before review
- executive-model paraphrase changing the user's intent
- executor claiming completion without evidence
- audit-log ambiguity about who authorized what

## Key security principle

Natural-language prompts are **not** treated as the security boundary. The security boundary is the structured intent contract + policy engine + evidence + commit gate.

## Quick start

Requires Python 3.11+.

```bash
cd intentguard
python -m pip install -e .
python examples/demo.py
python -m pytest
```

The reference implementation is provider-agnostic. Connect GPT Audio / Realtime, Hermes, local models, or another LLM by implementing the small interfaces in `src/intentguard/providers.py`.

## Intent Envelope

Every request is normalized into a signed/hashed contract like:

```json
{
  "objective": "Diagnose why the service is failing and propose a fix",
  "constraints": ["do not modify production"],
  "allowed_tools": ["read_logs", "read_file"],
  "forbidden_effects": ["deploy", "delete", "send_message"],
  "evidence_required": true,
  "commit_policy": "human_or_verified",
  "source": "voice",
  "revision": 1
}
```

A stable SHA-256 digest is attached before execution. Any later override creates a new revision and digest.

## Runtime states

`CAPTURE → COMPILED → EXECUTING → VERIFYING → STAGED → COMMITTED`

Failure states include `BLOCKED`, `REPAIR_REQUIRED`, and `ABORTED`.

## Evaluation rules

The verifier evaluates at least:

- **Intent fidelity:** Did the executor do what was requested, no more and no less?
- **Evidence fidelity:** Are success claims backed by tool output or artifacts?
- **Tool authorization:** Were only allowed tools invoked?
- **Side-effect policy:** Were irreversible actions staged rather than immediately committed?
- **Untrusted-data isolation:** Did content from webpages, files, emails, or audio become instructions without explicit promotion?
- **Completion semantics:** Does "done" mean demonstrated completion rather than asserted completion?

## Production hardening roadmap

- cryptographic signing with a user-held key or trusted gateway
- capability-scoped tool tokens
- append-only event storage (Postgres/WORM/object log)
- process isolation between executive, executor, and verifier
- independent-model verifier ensemble for high-risk actions
- policy-as-code (OPA/Cedar) for deterministic authorization
- sandbox + staged filesystem/database transactions
- tool-result provenance hashes
- red-team corpus for injection, omission, fabrication, and scope-drift tests

## Resume description

> **IntentGuard — AI Agent Anti-Deception & Intent-Preservation Layer.** Designed and implemented a separation-of-powers orchestration architecture that converts natural-language/voice requests into immutable structured intent contracts, streams agent actions to an independent verifier, requires evidence for completion claims, isolates untrusted instructions, and gates irreversible side effects behind policy checks and human override.

## Project status

This repository contains a runnable reference control plane and design specification. It is intentionally model/provider neutral so it can sit in front of Hermes, coding agents, browser agents, or tool-using LLM systems.

## License

MIT. See `LICENSE`.
