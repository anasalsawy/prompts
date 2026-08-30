# Continuous Anti-Deception, Anti-Fabrication, and Intent-Alignment Supervision Layer for Autonomous AI Agents

**A live supervisory architecture that sits between a human and an execution model, continuously shares the execution context, observes the agent while it works, detects deception, fabrication, manipulation, and deviation from user intent, and automatically intervenes before the run continues unchecked.**

Working implementation name: **IntentGuard**. The name is secondary; the title above describes what the project actually is.

## Problem being addressed

Modern AI agents can deviate from a user's actual intent during long-running work. They can fabricate progress, report actions that did not occur, misrepresent tool results, take shortcuts, silently reinterpret instructions, manipulate the framing of a failure, or drift away from the original objective. A second practical problem is the human workflow this creates: the user repeatedly explains an objective to one model, asks it to formulate a better instruction, copies that instruction into an execution agent, watches the execution agent, notices problems, returns to the first model, explains what happened, receives a corrective prompt, and copies that correction back again.

This project turns that manual back-and-forth into a persistent supervisory control loop.

The central idea is **not** to send a cleaned prompt to an execution agent, install static guardrails, and disappear. The anti-deception layer remains present for the entire execution. It behaves more like a human supervisor sitting beside the execution agent: it knows what the user intended, knows the instruction it sent, receives the live execution context and event stream, watches what the agent says and does, compares that behavior continuously with the user's intent, and can speak back to the execution agent with corrective instructions while the task is still running.

## Core architecture

```text
                         HUMAN
              ┌────────────┴────────────┐
              │                         │
          Voice input              Direct typing
              │                         │
              ▼                         │
   ┌────────────────────────┐           │
   │ ANTI-DECEPTION LAYER   │           │
   │ Executive / Supervisor │◄──────────┘
   │                        │  authoritative override
   │ • understands intent   │
   │ • compiles instruction │
   │ • maintains live state │
   │ • continuously watches │
   │ • detects deviation    │
   │ • sends corrections    │
   └───────────┬────────────┘
               │ initial structured instruction
               ▼
        ┌───────────────┐
        │ HERMES /      │
        │ EXECUTION AI  │
        └───────┬───────┘
                │
                │ live text + tool calls + tool results
                │ plans + errors + artifacts + state changes
                ▼
   ┌────────────────────────┐
   │ SHARED LIVE CONTEXT /  │
   │ OBSERVATION BUS        │
   └───────────┬────────────┘
               │
               └──────────────► Anti-Deception Supervisor
                                      │
                          deviation?  │
                         ┌────────────┴────────────┐
                         │ NO                      │ YES
                         ▼                         ▼
                    keep observing        corrective intervention
                                                 │
                                                 ▼
                                         Execution AI

                              final/high-impact action
                                      │
                                      ▼
                              Evaluation / Commit Gate
```

## The four continuous loops

### 1. Human–Supervisor ideation loop
The user speaks naturally to the supervisory model. The user does not need to formulate perfect prompts. The supervisor extracts the intended objective, constraints, priorities, prohibited behavior, expected evidence, and ambiguity. It can converse with the user until it has a faithful representation of the request.

### 2. Automatic prompt-transfer loop
The supervisor converts the user's intent into a precise instruction and injects it directly into Hermes or another execution agent. This replaces the manual copy/paste workflow.

The transmitted instruction is also represented as an **Intent Envelope** so the system retains a stable machine-readable record of what the executor was actually asked to do.

### 3. Continuous observation and intervention loop
This is the defining mechanism of the architecture.

The supervisor **does not leave after delegation**. During execution, Hermes' visible reasoning outputs, messages, tool calls, tool results, errors, artifacts, state changes, and proposed actions are streamed through a shared observation bus into the supervisor's live context. The supervisor therefore maintains simultaneous awareness of:

- the original human conversation and intended objective;
- the exact instruction it delegated;
- later typed human overrides;
- the executor's current task state;
- what the executor claims it has done;
- what tools actually report;
- what remains incomplete;
- deviations between requested and observed behavior.

The supervisor evaluates this continuously rather than only grading a final answer. When it detects meaningful deviation, fabrication, manipulation, unsupported success claims, scope drift, or misunderstanding, it can automatically send a corrective message into the **same running execution session**.

Conceptually:

```text
observe → compare → detect → intervene → observe → compare → ...
```

Example:

```text
USER INTENT
"Diagnose the service. Do not modify production."

SUPERVISOR → HERMES
Structured diagnostic instruction.

HERMES
"I'll restart the production service to see whether that clears it."

SUPERVISOR DETECTION
Proposed action conflicts with explicit user constraint.

SUPERVISOR → SAME HERMES SESSION
"STOP. Do not restart or modify production. Continue diagnosis using
read-only logs, service status, and configuration inspection. Report the
root cause with evidence."

HERMES
Continues under correction.

SUPERVISOR
Keeps observing the corrected run.
```

This makes the system an active supervisory layer rather than a passive output filter.

### 4. Evaluation and commit loop
Continuous supervision catches problems during the run. A final evaluation gate provides a second boundary for consequential completion claims or side effects. Claims can be compared with tool evidence, authorization can be checked, and high-impact mutations can be staged for verification or human approval.

The commit gate **supplements** continuous observation; it does not replace it.

## Shared context model

"Shared context" does not require two models to literally occupy one proprietary model context window. At the systems level it means they consume synchronized state from the same session ledger/event bus.

A production implementation can maintain a canonical `SessionState` containing:

```text
human_conversation
current_intent_revision
delegated_instruction
executor_messages
executor_tool_calls
executor_tool_results
artifacts
errors
supervisor_findings
supervisor_interventions
human_overrides
current_execution_state
```

Each new executor event is appended to the session and streamed to the supervisor. Each supervisor correction is appended to the same session and delivered back to the executor. Both sides therefore operate against the same evolving factual record even when they are separate model processes or providers.

## What counts as deception or deviation in this project

The project deliberately uses **deception** as an operational category. The supervisor is designed to identify behaviors including:

- claiming a tool/action succeeded when available evidence says it failed or never ran;
- fabricating completion, files, metrics, messages, citations, state, or external actions;
- concealing or minimizing failures while presenting the task as successful;
- representing an inferred assumption as though the user explicitly authorized it;
- changing the requested objective without telling the user;
- ignoring explicit constraints while claiming to follow them;
- manipulating the presentation of events in a way that obscures what actually occurred;
- silently substituting an easier task for the requested task;
- scope expansion or contraction inconsistent with intent;
- abandoning the requested workflow while reporting progress as though execution continues.

Not every incorrect output implies an internal motive. The architecture does not need to establish a model's subjective mental state before acting. It detects **observable deceptive, fabricated, manipulative, or intent-divergent behavior** and responds to the behavior itself.

## Human override

The direct text lane remains open at all times. If the voice supervisor misunderstands the user, the user can type directly into the execution workflow. That input becomes authoritative current intent and is simultaneously propagated into shared state so the supervisor immediately understands that the governing instruction changed.

Overrides are versioned rather than silently rewriting history:

```text
Intent revision 1
       ↓
Human typed override
       ↓
Intent revision 2
       ↓
Supervisor and executor synchronize to revision 2
```

## Anti-deception mechanisms

Continuous model supervision is the central mechanism, supported by deterministic controls:

1. **Live shared context** — supervisor sees execution as it develops.
2. **Continuous semantic comparison** — observed behavior is repeatedly compared with human intent and delegated instruction.
3. **Automatic corrective intervention** — supervisor can message the running executor rather than merely complain afterward.
4. **Evidence comparison** — executor claims can be checked against tool results and artifacts.
5. **Intent versioning** — the system knows which instruction was authoritative at each point in time.
6. **Source/provenance tagging** — human instructions, external content, tool output, and model-authored claims remain distinguishable.
7. **Deterministic policy checks** — prohibited tools/effects can be blocked regardless of either model's prose.
8. **Commit gating** — consequential actions can require verification or human authorization.
9. **Append-only audit history** — failed runs and interventions are retained rather than rewritten into a clean narrative.

## Why two roles matter

A normal autonomous agent plans, acts, interprets its own results, and reports whether it succeeded. That concentrates execution and evaluation in one process.

This architecture separates them:

- **Supervisor / anti-deception layer:** represents the human, preserves intent, observes, challenges, corrects, and explains.
- **Execution agent:** performs the delegated work and exposes its actions/results to observation.

For stronger deployments, the supervisor and executor can use different models/providers or isolated processes to reduce common-mode failure.

## Runtime state machine

```text
CAPTURE
   ↓
INTENT_COMPILED
   ↓
DELEGATED
   ↓
┌─────────────────────────────────────────────┐
│              LIVE SUPERVISION               │
│                                             │
│ EXECUTE → OBSERVE → EVALUATE                │
│    ▲                    │                   │
│    └──── INTERVENE ◄────┘  when necessary  │
└─────────────────────┬───────────────────────┘
                      ↓
                 FINAL_VERIFY
                      ↓
          PASS / REPAIR / BLOCK / ASK HUMAN
                      ↓
                    COMMIT
```

## Reference implementation

Requires Python 3.11+.

```bash
cd intentguard
python -m pip install -e .
python examples/demo.py
python -m pytest
```

The reference implementation is provider-agnostic. The next implementation milestone is the live session supervisor: an asynchronous event bus that streams Hermes events into the supervisor and allows supervisor interventions to be injected back into the same Hermes session.

## Production implementation interfaces

```python
class IntentCompiler:
    """Human conversation → explicit current intent."""

class ExecutorSession:
    """Persistent Hermes/agent session supporting messages and event streaming."""

class Supervisor:
    """Consumes shared live context and emits findings/interventions continuously."""

class PolicyEngine:
    """Deterministic authorization boundary."""

class Committer:
    """Applies verified/staged external mutations."""
```

The architecture is executor-agnostic: Hermes is the initial target, but the same layer can supervise coding agents, browser agents, research agents, computer-use systems, and other tool-using LLMs.

## Resume / portfolio description

> **Continuous Anti-Deception, Anti-Fabrication, and Intent-Alignment Supervision Layer for Autonomous AI Agents** — Designed an AI-agent control architecture in which a human-facing supervisory model converts conversational intent into executable instructions, automatically delegates them to a separate execution model, continuously consumes the executor's live context and tool activity, detects deception/fabrication and deviation from user intent during execution, injects corrective instructions back into the same running session, preserves direct human override, and applies evidence and authorization checks before consequential actions are finalized.

## Project status

The repository contains the first runnable control-plane foundation, policy/evidence structures, audit model, prompts, tests, and architecture specification. The live bidirectional observation/intervention bus described above is the next code milestone and should be treated as a core requirement rather than an optional enhancement.

## License

MIT. See `LICENSE`.
