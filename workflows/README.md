# Cosmos Workflow Engine Next Steps

This folder is for Cosmos workflow definitions and, later, a reusable workflow engine.

The first draft workflow is:

```text
workflows/cosmos-improvement-triage.yaml
```

It is inspired by:

```text
https://github.com/tonbistudio/hermes-multi-agent-workflow.git
```

## Current state

- Reference repo cloned locally under `/opt/data/Cosmos/external/hermes-multi-agent-workflow`.
- Reference repo validated with `uv run --with PyYAML python -m cli.triage validate`.
- Reference repo tests passed: 12/12.
- Cosmos-specific workflow config drafted, not active yet.

## Why this matters

Cosmos needs reusable pipelines, not only one-off agents. A workflow config gives the CEO agent a reliable way to run repeated work:

```text
intake → dedup → score → research fan-out → route → human gate → fulfill → deliver
```

## Activation requirements

Before this becomes live:

1. Decide whether to run the reference engine directly or copy the generic engine into Cosmos.
2. Create/confirm Hermes profiles referenced in `roles:`.
3. Create scout/orchestrator skills for Cosmos-specific intake.
4. Connect to a Hermes Kanban board.
5. Dry-run on one sample improvement item.
6. Keep a single human approval gate before fulfillment.

## Safety rule

Do not auto-approve workflow fulfillment. The workflow may research and prepare proposals automatically, but any build/integration/external action should pause at the gate unless Ram explicitly grants that workflow a higher autonomy level.
