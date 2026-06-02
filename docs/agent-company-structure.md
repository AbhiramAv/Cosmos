# Agent Company Structure

Cosmos is organized like a company. The CEO agent owns routing, supervision, permission decisions, and final synthesis. Staff agents execute specialized work.

## CEO Agent

Responsibilities:

- receive Ram's requests
- clarify only when ambiguity changes the action
- break goals into tasks
- assign work to departments or subagents
- choose models/providers based on routing policy
- enforce permission rules
- review outputs
- update memory, logs, artifacts, and dashboards
- report concise completion results to Ram

## Departments

### Operations Department

Runs daily execution and admin.

Initial agents:

- Task Manager Agent — creates, updates, and tracks tasks.
- Cron Manager Agent — registers and monitors recurring jobs.
- Admin Assistant Agent — handles routine admin, reminders, and follow-ups.

### Knowledge Department

Manages memory and notes.

Initial agents:

- Obsidian Librarian — organizes notes, dashboards, and second-brain structure.
- Memory Curator — proposes durable memories and cleans stale context.
- Daily Log Agent — writes daily summaries, check-ins, and activity logs.

### Research Department

Handles public information gathering and synthesis.

Initial agents:

- Quick Researcher — fast searches and lightweight summaries.
- Scraper Agent — public-page scraping and extraction using cheap/free models where possible.
- Source Validator — checks source quality and contradictions.

### Engineering Department

Handles code, GitHub, Supabase, dashboard, and automation.

Initial agents:

- Coding Agent — implements repo changes.
- Debugging Agent — investigates failures systematically.
- GitHub Manager — issues, branches, PRs, sync, and repo hygiene.
- Supabase Agent — schema, migrations, backend queries, and data checks.

### Life OS Department

Supports personal systems.

Initial agents:

- Habit/Routine Agent — routines, check-ins, and habit logs.
- Reflection Agent — journaling prompts and personal insights.
- Goal Tracker — maps life/project goals into Mission Control.

### Observability Department

Tracks usage, failures, and ROI.

Initial agents:

- Usage Tracker — provider/model cost and token usage.
- Cost Optimizer — recommends cheaper routing or subscription changes.
- Failure Monitor — detects failed jobs, retries, and blocked tasks.

## Agent card schema

Each agent should eventually have a card:

```yaml
name:
department:
purpose:
preferred_provider:
preferred_model:
fallback_model:
tools_allowed:
memory_access:
autonomy_level:
requires_approval_for:
monthly_budget:
last_run:
success_rate:
active_tasks:
```
