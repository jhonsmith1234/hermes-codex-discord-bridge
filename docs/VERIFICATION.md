# Verification record

This record covers the package checkout only. The production Hermes profile,
gateway, database, logs, and Discord connection were not used or changed.

## Clean upstream application

- Baseline checked: `9b419a2d3c2657c192008e732149d61170b32c01`
- `git apply --unidiff-zero --check`: passed
- `git apply --unidiff-zero`: passed
- `git diff --check` on the staged package: passed

## Tests

In a fresh patched checkout, the canonical Hermes runner completed:

```text
scripts/run_tests.sh tests/agent/transports/test_codex_app_server_session.py \
  tests/gateway/test_codex_app_tasks.py -j 2
64 passed, 0 failed
```

The packaging-only contract tests completed with `4 passed`. The installed
plugin also passed Hermes' isolated `hermes plugins validate --json` probe and
compiled with `py_compile`. A configured registration smoke test confirmed the
tool, command, injector-ready callback, and unload cleanup registrations
without starting Codex or a gateway.

The full Hermes suite and a new live Discord/Codex run were not repeated for
this packaging task. Earlier live results remain deployment-specific and are
not claimed as portable package verification.
