# Provider Routing Policy

Cosmos should be model-agnostic and cost-aware.

## Current known providers

- OpenAI: paid
- Claude/Anthropic: paid
- OpenRouter: $20 budget plus free models
- Future: local models or additional free/cheap providers

## Routing tiers

### Tier 0 — Free/OpenRouter free

Use for:

- public scraping
- simple extraction
- basic summarization
- note cleanup
- classification/tagging
- routine cron processing
- drafts that will be reviewed

Avoid:

- sensitive personal data
- final decisions
- complex architecture
- high-stakes writing

### Tier 1 — Cheap OpenRouter paid

Use for:

- moderate summaries
- batch analysis
- non-sensitive research
- repeated background jobs

### Tier 2 — OpenAI / Claude

Use for:

- deep reasoning
- synthesis
- architecture
- personal context
- final review
- permission decisions
- CEO summaries

### Tier 3 — Coding agents

Use Claude Code, Codex, OpenCode, or similar for:

- implementation
- debugging
- PRs
- code review
- repo refactors

## Routing metadata to track

```yaml
task_id:
agent:
provider:
model:
reason_for_choice:
estimated_cost:
actual_cost:
latency:
quality_score:
should_have_used_cheaper_model:
```

## Budget rules

- Prefer free/cheap for low-risk repetitive work.
- Escalate to premium when quality or sensitivity matters.
- Track cost by provider, model, agent, mission, and month.
- Flag waste when expensive models handle routine work.
