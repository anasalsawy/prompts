# AI Agent Systems, Research Architectures, and Prompt Library

This repository is the umbrella workspace for smaller agent experiments, reusable system prompts, architectural notes, and projects that are not yet large enough to justify a dedicated repository.

Major independent systems should live in their own repositories. Small experiments and reusable prompt assets should be consolidated here rather than creating many low-signal repositories.

## Major standalone projects

These are substantial enough to remain independent portfolio repositories:

- **Dialogue OS** — conversational operating-system/runtime work.
- **Dual Lobe** — multi-model / dual-process agent architecture.
- **Continuous Runtime-Synchronized Deception Detection and Intent-Preservation Supervision for Autonomous AI Agents** — continuous anti-deception supervision using shared human intent, independent runtime observation, active intervention, and an OpenRouter-compatible model-gateway direction. Architecture seed: [`continuous-runtime-deception-supervision/`](./continuous-runtime-deception-supervision/).
- **Browser-use integration / browser control system** — browser-use bridge, browser specialist, inline-pane/runtime control, and related browser-agent infrastructure should be consolidated as one major browser repository rather than split into small browser repos.
- **VAPI + Twilio voice-agent integration** — phone/voice plugin and realtime calling infrastructure should remain a dedicated project when its current source is consolidated.
- **LeadPilotAI** — autonomous lead-finding/runtime project.
- **Your Travel Agent** — production travel-agent system.

## Umbrella projects and smaller experiments

Smaller prototypes, one-off agent roles, prompt packs, tests, task-specific experiments, and early architectural sketches belong here. Examples include:

- Chief Orchestrator
- Builder Lead
- Researcher
- Customer Support & Communications
- Browser Operator / Booker / Shopper prompt assets
- Verifier / Auditor
- Internal Structor / State Manager
- Governor / Policy Authority
- YTA multi-agent system prompts
- early supervisory prototypes such as `intentguard/`

## Repository organization policy

A project should graduate to its own repository when it has at least one of the following:

1. a distinct runtime or application;
2. a reusable integration/API/plugin boundary;
3. an independent research architecture with its own implementation roadmap;
4. a deployable service or desktop/CLI product;
5. enough code and documentation that it is meaningful as a standalone portfolio project.

Tiny test repos, single-task experiments, generated variants, and duplicates should instead be folded into this umbrella repository or into the major project they belong to.

## Current consolidation candidates

The following existing repositories appear small, duplicated, task-specific, or closely related to larger systems and should be reviewed for consolidation rather than presented as major standalone portfolio projects:

- `Pj`
- `builder-agent-task1` → fold into `builder-agent`
- `yta-assistant-travel-memory` → fold into the primary Your Travel Agent project
- `your-travel-agent-new` → empty/duplicate candidate
- `browser-specialist-a2a` → fold into the primary browser-use integration repository
- related browser bridge/specialist experiments → one browser-use repository

No destructive migration is implied by this list; preserve history until each project has been copied and verified in its destination.

## New architecture

The current research architecture is:

### Continuous Runtime-Synchronized Deception Detection and Intent-Preservation Supervision for Autonomous AI Agents

A model-gateway and local runtime-observation system that continuously compares an autonomous agent's actual execution trajectory with authoritative human intent, detects deception, fabricated success, hidden failure, manipulation, and intent deviation, and injects corrective instructions into the same active session.

See [`continuous-runtime-deception-supervision/`](./continuous-runtime-deception-supervision/).
