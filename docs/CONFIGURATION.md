# Installation and configuration

The commands below use placeholders. Replace them with paths and identifiers
from the target installation; do not commit the resulting profile config.

## 1. Prepare a clean Hermes checkout

```bash
git clone https://github.com/NousResearch/hermes-agent.git hermes-agent
cd hermes-agent
git checkout 9b419a2d3c2657c192008e732149d61170b32c01
git diff --exit-code
git apply --unidiff-zero --check /path/to/hermes-codex-discord-bridge/patches/0001-codex-discord-bridge.patch
git apply --unidiff-zero /path/to/hermes-codex-discord-bridge/patches/0001-codex-discord-bridge.patch
```

Install Hermes' normal dependencies using its documented setup. The bridge
does not add a new secret environment variable or a separate database service.

## 2. Install the profile plugin

For the profile that owns the Discord bot, copy the directory
`plugin/codex_tasks/` to that profile's plugin directory, for example:

```text
<hermes-profile-home>/plugins/codex_tasks/
```

The directory must contain both `plugin.yaml` and `__init__.py`. A profile
home may be the default Hermes home or a named profile home; use the actual
profile selected by the gateway rather than a hardcoded home path.

## 3. Add profile configuration

Merge the contents of
[`examples/ownerreview-config.yaml`](../examples/ownerreview-config.yaml) into
the target profile's `config.yaml`. Set at least:

- `owner_conversation_id`: the Discord DM identifier that is allowed
  to submit and answer tasks;
- `cwd`: the workspace in which Codex app-server tasks may run;
- `profile`: the exact Hermes profile name serving that DM.

Set `allow_gateway_injection: true` only for this reviewed plugin entry. The
plugin uses this explicit host permission to send a completion or waiting
notice back into the existing gateway session.

If the gateway's Discord slash-access policy defines
`gateway.platforms.discord.extra.user_allowed_commands`, add both
`codex-respond` and `codex-recover` to that list. Otherwise the built-in
admin-only gate will reject the recovery command before the plugin receives
it, even when the request comes from the configured owner DM.

The Discord bot token, Codex authentication, and any MCP credentials remain in
the target installation's normal secret stores. They are not part of this
configuration example.

## 4. Verify before starting the gateway

From the patched Hermes checkout, use its canonical runner:

```bash
git diff --check
scripts/run_tests.sh tests/agent/transports/test_codex_app_server_session.py \\
  tests/gateway/test_codex_app_tasks.py
```

Also compile the installed plugin without importing the live gateway:

```bash
python -m py_compile <hermes-profile-home>/plugins/codex_tasks/__init__.py
HERMES_HOME=/tmp/hermes-plugin-validate hermes plugins validate \
  <hermes-profile-home>/plugins/codex_tasks --json
```

Review `hermes plugins list` and confirm that only the intended profile has
`codex_tasks` enabled. Do not use a production database or gateway restart as
a substitute for the clean-checkout tests.

## 5. Use the bridge

The model-facing tool is `codex_task_submit`. It accepts a bounded purpose,
scope, completion conditions, and optional steps/services. After acceptance,
the Hermes turn waits for the asynchronous Codex result.

For a Codex command or file approval, use the existing gateway commands:

```text
/approve [<task_id> <server_request_id>] [once|session]
/deny [<task_id> <server_request_id>]
```

For structured input or MCP elicitation, answer the exact live request:

```text
/codex-respond <task_id> <server_request_id> '<JSON response>'
```

The notification includes the request and server-request identifiers. The
answer is validated against the live request and resumes the same Codex turn;
guessing an ID or answering from another DM is rejected.

If a gateway restart loses the live app-server session, the task is marked
`unknown` and is never replayed automatically. Use the owner-DM recovery
command after reviewing the original request:

```text
/codex-recover status <task_id>
/codex-recover inspect <task_id>
/codex-recover retry <task_id> RETRY
/codex-recover cancel <task_id> CANCEL
```

`inspect` only reads the persisted Codex thread and may settle a terminal task;
it never starts a new turn. `retry` is an explicit new Codex turn and may
duplicate effects from the unknown run. `cancel` records a local cancellation
and does not claim that an already-lost external process was cancelled.
These commands are accepted only in the configured owner DM and profile.

## Removal and rollback

1. Stop the target gateway through its normal operator procedure.
2. Remove the `codex_tasks` entry from `plugins.enabled` and
   `plugins.entries`, then remove the profile plugin directory.
3. Preserve the private task database if you need to inspect unresolved work;
   it is runtime state and must not be committed. If it is no longer needed,
   archive or delete it using the operator's normal data-retention policy.
4. To remove the core integration, restore the clean pinned checkout or create
   a fresh checkout at the pinned commit. Do not use a destructive reset on a
   worktree containing unrelated operator changes.

Pending tasks lost with a gateway restart are intentionally not auto-replayed;
use the owner-DM recovery commands above to inspect the recorded state before
deciding whether to retry the underlying work manually.
