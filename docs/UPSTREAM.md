# Upstream policy

The package targets Hermes Agent commit
`9b419a2d3c2657c192008e732149d61170b32c01`.

Before applying the patch:

```text
git rev-parse HEAD
git diff --exit-code
```

The first command must print the pinned commit and the second must report a
clean tree. Because the distribution patch is intentionally context-minimal,
apply it with `git apply --unidiff-zero --check` followed by
`git apply --unidiff-zero`.

The patch deliberately carries only the Codex app-server session extensions,
the durable task bridge, the delivery-receipt integration, the plugin loading
boundary changes, and their regression tests. It does not copy a Hermes
profile, runtime state, credentials, logs, or deployment configuration.

When upstream changes, regenerate or re-review the patch against the new base;
do not silently apply it with three-way conflict resolution. Record the new
baseline and rerun the clean-checkout tests before distribution.
