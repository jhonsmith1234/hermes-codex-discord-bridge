# Hermes–Codex–Discord bridge

This repository packages an experimental Hermes Agent integration for a private
Discord owner DM. It consists of a pinned Hermes core patch and a configurable
user-profile plugin. It is not a replacement for Hermes Agent and is not a
standalone Codex client.

The supported flow is:

`Discord owner DM → Hermes plan → durable SQLite task → Codex app-server thread/turn → owner approval or input → completion notification`

The plugin derives routing identity from authenticated Hermes gateway session
context. Model arguments cannot choose the recipient, profile, or conversation.
Approval, structured user input, and MCP elicitation are held for an explicit
owner response; they are not auto-approved.

## Compatibility

- Upstream project: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Required baseline: `9b419a2d3c2657c192008e732149d61170b32c01`
- Platform covered here: Discord on macOS
- The patch is intentionally tied to the baseline above. Review and rebase it
  before applying it to another Hermes revision.

The upstream MIT notice is retained in [LICENSE](LICENSE), with attribution in
[NOTICE](NOTICE).

## Repository contents

- `patches/0001-codex-discord-bridge.patch`: core changes, the durable bridge
  module, and regression tests.
- `plugin/codex_tasks/`: portable profile plugin (`plugin.yaml` plus
  `__init__.py`).
- `examples/ownerreview-config.yaml`: configuration shape with placeholders only.
- `docs/CONFIGURATION.md`: installation, configuration, verification, and
  removal instructions.
- `docs/UPSTREAM.md`: baseline and patch policy.

No credentials, `.env` files, database files, logs, conversation records,
account configuration, or deployment-specific paths are included.

## Installation summary

Apply the patch to a clean checkout of the exact baseline, then install the
plugin into the profile that owns the Discord bot. Configure the owner DM ID,
Codex working directory, and optional Codex binary/home in that profile's
`config.yaml`. Keep Discord and Codex credentials in their normal local secret
stores; do not put them in this repository.

Follow [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for the complete,
reversible procedure.

## Guarantees and limits

- Duplicate Discord events are deduplicated by the durable task store.
- Task, server-request, origin, and sender identities are checked before an
  answer resumes a live Codex turn.
- A successful platform send is recorded from the adapter's send receipt and
  linked to the notification generation; gateway acceptance alone is not
  treated as delivery.
- A pending live request lost during gateway restart is marked unknown and is
  not automatically replayed.
- Unknown tasks can be inspected read-only, explicitly retried, or cancelled
  from the authenticated owner DM with `/codex-recover`; retry requires the
  literal `RETRY` confirmation because duplicate external effects are possible.
- Long or interrupted multi-message sends remain at-least-once; exactly-once
  delivery is not promised.
- Google Docs creation/editing and arbitrary third-party deployments are not
  covered by this package's verification.

This repository is public. Keep Discord, Codex, and MCP credentials in their
normal local secret stores; never commit them to this repository.
