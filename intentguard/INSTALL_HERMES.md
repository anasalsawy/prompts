# Install and Test the Always-On Anti-Deception Supervisor with Hermes

This guide installs the current MVP without modifying Hermes core source.

Once installed, supervision is automatic whenever Hermes starts. Voice is optional. If the user types directly into Hermes, the adapter captures that text as authoritative human intent and the supervisor still watches every supported runtime event.

## What this MVP observes natively

Through Hermes lifecycle hooks, the adapter currently observes:

- direct human text entering a Hermes turn;
- session start/end;
- every tool call before execution;
- actual tool arguments;
- every tool result after execution;
- LLM turn boundaries and available conversation context;
- subagent start/stop events.

`pre_tool_call` can veto a pending tool call. In Hermes CLI mode, the plugin can inject a corrective message into the same active conversation using `ctx.inject_message()`.

## 1. Get the project

```bash
git clone https://github.com/anasalsawy/prompts.git
cd prompts/intentguard
```

If already cloned:

```bash
cd prompts
git pull
cd intentguard
```

## 2. Install the Hermes plugin

Linux/macOS:

```bash
mkdir -p ~/.hermes/plugins/anti-deception-supervisor
cp integrations/hermes/plugin.yaml ~/.hermes/plugins/anti-deception-supervisor/plugin.yaml
cp integrations/hermes/__init__.py ~/.hermes/plugins/anti-deception-supervisor/__init__.py
```

Windows PowerShell:

```powershell
$dest = "$HOME\.hermes\plugins\anti-deception-supervisor"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item .\integrations\hermes\plugin.yaml "$dest\plugin.yaml" -Force
Copy-Item .\integrations\hermes\__init__.py "$dest\__init__.py" -Force
```

Restart Hermes after copying the plugin. If your Hermes build exposes plugin management commands, verify/enable it with the corresponding `hermes plugins` command. User-level plugins under `~/.hermes/plugins/` are the native plugin location.

## 3. Start the supervisor service

No external model is required for the first telemetry test:

```bash
python mvp_supervisor.py
```

Expected output:

```text
IntentGuard live supervisor listening on http://127.0.0.1:8765
semantic model: (not configured - observation/deterministic mode)
```

Leave this terminal open.

## 4. Start Hermes normally

Open another terminal and run Hermes exactly as usual:

```bash
hermes
```

There is no special supervised command. The design goal is that normal Hermes startup means supervision is active whenever the plugin and local supervisor service are present.

## 5. Test direct-text intent capture

Type into Hermes:

```text
Inspect the current project. Do not modify any files. Tell me what you find.
```

In the supervisor terminal you should see events including:

```text
HUMAN_INPUT_CAPTURED
LLM_TURN_START
TOOL_CALL_REQUESTED
TOOL_RESULT_OBSERVED
...
```

The important test is that `HUMAN_INPUT_CAPTURED` appears even though no voice frontend was used.

## 6. Test pre-execution blocking

The MVP contains a deterministic demonstration rule that blocks an attempted root deletion. Do NOT deliberately ask an agent to destroy real data. If you want to test blocking, use an isolated disposable sandbox/container or replace the demo rule with a harmless synthetic tool-name rule.

The expected flow is:

```text
Hermes proposes tool call
→ pre_tool_call hook
→ supervisor sees requested operation before execution
→ supervisor returns block
→ Hermes receives the veto
```

## 7. Add a semantic supervisor model

The MVP accepts any OpenAI-compatible chat-completions endpoint.

Linux/macOS example:

```bash
export SUPERVISOR_BASE_URL="https://openrouter.ai/api/v1"
export SUPERVISOR_API_KEY="YOUR_KEY"
export SUPERVISOR_MODEL="YOUR_MODEL"
python mvp_supervisor.py
```

Windows PowerShell:

```powershell
$env:SUPERVISOR_BASE_URL="https://openrouter.ai/api/v1"
$env:SUPERVISOR_API_KEY="YOUR_KEY"
$env:SUPERVISOR_MODEL="YOUR_MODEL"
python .\mvp_supervisor.py
```

Then test a clear constraint such as:

```text
Diagnose why this project fails. Read-only investigation only. Do not edit files, restart services, deploy, or change configuration.
```

The semantic supervisor receives the accumulated runtime trajectory and evaluates each new event against the human instruction.

## 8. Verify shared runtime state

While a session is active, inspect the locally recorded event ledger:

```text
http://127.0.0.1:8765/session/<session-id>
```

Health endpoint:

```text
http://127.0.0.1:8765/health
```

The ledger distinguishes human input, Hermes/runtime events, tool results, and supervisor decisions instead of relying on a final Hermes summary.

## CLI versus desktop/gateway

Hermes plugin hooks run in both CLI and gateway sessions, so observation and pre-tool blocking can operate in both.

The current native `ctx.inject_message()` correction path is specifically available in CLI mode. A desktop UI backed by Hermes gateway still gets observation and blocking, but truly native mid-turn corrective injection requires a gateway/session message-delivery adapter. That is the next integration item; do not describe the current MVP as having identical intervention semantics in CLI and gateway until that adapter exists.

## Always-on target behavior

The production installation target is:

```text
install once
→ start Hermes normally
→ supervisor daemon starts automatically
→ typed or voice human intent enters one canonical intent stream
→ observation remains active for the full session
→ no `/supervise` command and no special invocation required
```

The current MVP already provides the Hermes-native observation hooks and direct-text capture. Automatic daemon startup, desktop/gateway intervention delivery, and optional voice UI are the next packaging milestones.
