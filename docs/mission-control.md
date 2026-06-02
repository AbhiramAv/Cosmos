# Mission Control

Mission Control tracks goals that are bigger than one chat turn but smaller than vague life ambitions.

## Mission types

- Short-term goal: one session or one day.
- Mid-term mission: days/weeks with multiple actions.
- Long-term north star: life/project direction reviewed periodically.

## Mission schema

```yaml
title:
status: active | paused | completed | blocked | cancelled
why_it_matters:
target_outcome:
deadline:
owner: Ram + Cosmos CEO
assigned_agents:
ram_actions:
cosmos_actions:
blocked_items:
next_actions:
related_tasks:
related_artifacts:
related_obsidian_notes:
related_github_repos:
progress_log:
```

## Workflow

1. Ram gives a goal.
2. Cosmos asks only critical clarification questions.
3. Cosmos creates a mission brief.
4. Cosmos separates Ram actions from agent actions.
5. Agents execute safe actions.
6. Mission Control updates progress.
7. Dream Agent reviews missions nightly and suggests next moves.

## Example mission

```yaml
title: Build Cosmos Agentic OS v1
why_it_matters: Reduce repeated manual work and create a scalable personal AI operating layer.
target_outcome: Blueprint, Obsidian structure, dashboard spec, Supabase schema, and first automations.
assigned_agents: [CEO Agent, Knowledge Department, Engineering Department, Observability Department]
ram_actions: [Provide Obsidian path, choose Supabase project, approve dashboard direction]
cosmos_actions: [Create docs, draft schema, propose cron jobs, maintain GitHub sync]
```
