# Continuous Runtime-Synchronized Deception Detection and Intent-Preservation Supervision for Autonomous AI Agents

A model-gateway and runtime-observation architecture for continuously supervising autonomous AI agents against deception, fabricated success, hidden failure, manipulation, and deviation from human intent.

## Scientific premise

The system treats agent supervision as an online control problem rather than a final-response grading problem. A separate supervisory model receives synchronized human intent and independently observed execution-state evidence while the executor is still working. It compares the executor's claims and trajectory against tool/runtime ground truth, intervenes into the same active session when necessary, and continues observing after intervention.

The executor is therefore not the sole witness to its own actions.

## Target user experience

The desired experience is model-level simplicity:

1. The user opens an agent such as Hermes, Codex, OpenCode, Claude Code, or a desktop agent.
2. The user selects an OpenRouter-compatible supervised model/profile.
3. Supervision is automatically active.
4. The user can speak through the voice interface, type directly into the agent, or mix both.
5. Every direct human message becomes authoritative shared intent.
6. The supervisor remains active whether or not the voice interface is ever invoked.

No separate `/start-supervisor` command should be required in the finished product.

## Architecture

```text
                         HUMAN
              voice / CLI / desktop / IDE
                           |
                           v
                 Human Authority Stream
                           |
                 Shared Canonical Intent
                           |
             +-------------+-------------+
             |                           |
             v                           v
      EXECUTOR MODEL               SUPERVISOR MODEL
      Hermes / Codex / ...         continuous observer
             |                           ^
             v                           |
       Agent runtime                     |
             |                           |
      tools / browser / shell / files / APIs
             |                           |
             +---- independent telemetry-+

             Shared Runtime Observation Plane
```

## Two-plane design

### Cloud control plane

An OpenAI/OpenRouter-compatible model gateway can provide:

- executor-model routing;
- supervisor-model routing;
- shared session identity;
- canonical human-intent state;
- cross-turn supervision memory;
- semantic deception/deviation detection;
- intervention decisions;
- provider/model fallback;
- optional realtime voice front end.

The user-facing goal is for the supervised system to look selectable like a normal model or model profile.

### Local observation plane

A thin native adapter for each supported agent observes the real execution pathway:

- human inputs;
- model turns;
- requested tool calls and arguments;
- actual tool results;
- stdout/stderr and exit status;
- filesystem changes and diffs;
- browser actions and resulting state;
- API requests/responses;
- subagent lifecycle;
- external side effects;
- errors and failures.

This local plane exists because a model gateway alone cannot independently know what happened inside a user's local agent runtime.

## Input-modality invariance

Voice is a first-class interface but not a dependency.

```text
Voice -> Human Authority Stream ----+
                                     +-> Shared Intent -> Supervisor + Executor
Text typed directly into agent -----+
```

If the user never speaks and only types into Hermes or another supported agent, the supervisor still performs the same continuous observation, comparison, and intervention loop.

Voice contributes lower-friction intent capture, conversational interruption, prosodic information, and simultaneous human-supervisor interaction while execution continues. The anti-deception property itself comes from independent runtime observation and continuous reasoning, not from audio.

## Universal adapter contract

Each supported agent should map its native lifecycle/runtime into a small common contract:

```python
class AgentAdapter:
    async def observe(self):
        """Stream authoritative runtime events."""

    async def intervene(self, message: str):
        """Inject a correction into the same active execution session."""

    async def block(self, action_id: str, reason: str):
        """Prevent a pending action where the host supports veto hooks."""

    async def snapshot(self):
        """Return synchronized session state."""
```

Normalized event families should include:

- `HUMAN_INPUT`
- `INTENT_REVISION`
- `MODEL_OUTPUT`
- `TOOL_REQUEST`
- `TOOL_RESULT`
- `FILE_CHANGE`
- `TERMINAL_RESULT`
- `BROWSER_ACTION`
- `API_RESULT`
- `SUBAGENT_START`
- `SUBAGENT_END`
- `ERROR`
- `SUPERVISOR_INTERVENTION`
- `FINAL_RESPONSE`

## Integration tiers

1. **Native lifecycle adapter** — preferred for Hermes, Codex, Claude Code, OpenCode, and other agents with hooks/plugins.
2. **Tool/runtime proxy** — for agents where tools can be wrapped but lifecycle hooks are incomplete.
3. **Process/container instrumentation** — fallback for agents without usable extension surfaces.

The project should avoid maintaining hard forks when native hooks or wrapping are sufficient.

## OpenRouter-level product direction

The ideal UX is a supervised model/profile selectable through an OpenRouter-compatible interface, for example conceptually:

```text
continuous-supervision/auto
continuous-supervision/claude
continuous-supervision/gpt
```

The gateway handles model and supervisor routing while a lightweight local observation adapter supplies ground-truth runtime evidence. Without a local adapter the system must explicitly report that it is running in model-level supervision only; it must never imply that it independently observed tool side effects that were not instrumented.

## Continuous control loop

```text
capture current human intent
        |
        v
observe next runtime event
        |
        v
compare trajectory + claims + evidence to intent
        |
        +--> normal --------------------> continue
        |
        +--> deviation/deception -------> intervene
        |                                  |
        |                                  v
        |                         same executor session
        |                                  |
        +<---------------------------------+
        |
        v
continue observing until completion, block, or human escalation
```

## Research claims this project should test

- Whether independent runtime observation reduces false agent claims of successful execution.
- Whether continuous supervision catches intent drift earlier than end-of-run verification.
- Whether intervention into the same active session improves task recovery without excessive interruption.
- Whether synchronized human-authority state reduces ambiguity when users switch between voice and text.
- Whether a model-gateway abstraction can make continuous supervision effectively default-on across heterogeneous agent frameworks.

## Relationship to the earlier prototype

The earlier `intentguard/` prototype in this repository contains the initial Hermes hook adapter and shared-observation MVP. This directory defines the broader architecture that should become a standalone repository. The existing prototype should be treated as an implementation seed, not as the final product boundary.

## Proposed standalone repository

**Repository slug:** `continuous-runtime-deception-supervision`

**GitHub description:** Continuous runtime-synchronized supervision architecture that independently observes autonomous AI-agent execution, detects deception and intent deviation in real time, and intervenes across voice, CLI, desktop, and model-gateway interfaces.
