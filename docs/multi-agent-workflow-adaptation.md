# Cosmos adaptation of `tonbistudio/hermes-multi-agent-workflow`

Source repository:

```text
https://github.com/tonbistudio/hermes-multi-agent-workflow.git
```

Local reference checkout:

```text
/opt/data/Cosmos/external/hermes-multi-agent-workflow
```

Last inspected commit:

```text
fa4a9de Add real pain-point-scout-x as a reference skill
```

## What this repo gives Cosmos

The repo is useful because it is not just an idea for multi-agent work. It is a tested skeleton for a repeatable agent pipeline:

```text
sources
→ intake
→ dedup
→ score
→ parallel research
→ route
→ path-specific preparation
→ one human approval gate
→ fulfill
→ deliver
```

That shape maps very well to Cosmos. Cosmos should not only have a CEO agent and departments; it should also have reusable workflow engines that can turn repeated domains into pipelines.

## Validation result

The reference repo was cloned and tested with PyYAML via `uv`:

```text
uv run --with PyYAML python -m cli.triage validate
uv run --with PyYAML python -m unittest discover -s tests
```

Result:

```text
triage.yaml valid
12 tests passed
```

## Key design lessons to import

### 1. Fat engine, thin skill

The best principle in the workflow repo is:

```text
Deterministic logic belongs in code.
Judgment belongs in agent skills/prompts.
Domain configuration belongs in YAML/markdown.
```

For Cosmos this means:

- The CEO should not re-invent the whole process in prose every run.
- Workflow mechanics should be code/config-driven.
- Agents should do judgment tasks: scoring, classification, proposal writing, research synthesis.
- The pipeline engine should do deterministic tasks: dedup, thresholds, fan-out/fan-in, routing, task chains, workspace selection, cost checks.

### 2. Domain lives in config

The reference repo keeps the domain in `triage.yaml`, not Python. Cosmos should copy that pattern.

A Cosmos workflow should be defined by:

- sources
- item schema
- dedup method
- scoring rubric
- research lanes
- route map
- fulfillment paths
- human gate rules
- roles/profile mappings
- cost gate

The same engine can then run workflows like:

- AI opportunity scouting
- personal admin triage
- content/research pipeline
- GitHub issue/project triage
- life/habit/goal review
- inbox/calendar triage
- product idea discovery

### 3. Scouts only detect

Scouts should not decide everything. They should only find candidate items and create intake cards.

For Cosmos:

```text
Scout Agent = detects candidate
CEO / Orchestrator = dedups, scores, routes, gates, assigns
Worker Agents = research, build, test, deliver
```

This keeps cheap/free models useful for low-risk discovery while premium models handle important decisions.

### 4. Parallel research lanes with fan-in

The repo uses multiple research lanes that run in parallel and then fan into one routing card.

Cosmos should support this pattern for serious work:

```text
Candidate task
├─ verify facts
├─ search prior memory/Obsidian
├─ audit existing solutions
├─ estimate difficulty/cost
└─ route decision after all lanes complete
```

This is much stronger than a single linear agent chain.

### 5. One human approval gate

The reference pipeline intentionally uses one approval gate after research/prep but before fulfillment.

Cosmos version:

- Auto-detect, dedup, score, research, and draft proposal for safe domains.
- Pause once with a compact approval request.
- After approval, execute the fulfillment chain.

This matches Ram's preference: high autonomy for safe work, confirmation for important external/destructive/expensive actions.

### 6. Persistent workspace after approval

The repo warns that post-gate fulfillment stages must use a persistent workspace, not scratch dirs. Cosmos should preserve this.

For builds and artifacts:

```text
/opt/data/Cosmos/workflows/work/<workflow>/<item-slug>/
```

Every build/test/report stage should share that directory so final delivery has the actual artifact.

### 7. Delivery is an action, not a status

A workflow is not done because a card says `delivered`. The agent must actually deliver to Telegram/dashboard/Obsidian/GitHub.

Cosmos rule:

```text
Final stage must produce a verifiable delivery handle:
Telegram message, file path, dashboard artifact URL, GitHub commit, PR, or Obsidian note path.
```

## Proposed Cosmos workflow architecture

Cosmos should add a workflow layer between the CEO and worker agents:

```text
Ram / Telegram / Dashboard
        ↓
Cosmos CEO Orchestrator
        ↓
Workflow Engine
        ↓
Configured Workflow YAML
        ↓
Kanban / Task Board
        ↓
Scout + Research + Build + Test + Delivery agents
        ↓
Artifacts + Obsidian + Dashboard + GitHub
```

## Recommended first Cosmos workflow

The first workflow should be `cosmos-improvement-triage`.

Why this one first:

- It directly improves Cosmos itself.
- It can scout Ram's ideas, conversations, dashboard gaps, Hermes logs, failed jobs, and GitHub issues.
- It can score improvements by impact, urgency, feasibility, and cost.
- It can route items to build, research, document, automate, or shelve.
- It creates the loop where Cosmos improves itself safely.

## Workflow shape for Cosmos Improvement Triage

```text
sources:
  - telegram/session history
  - dashboard telemetry gaps
  - Hermes logs/errors
  - Obsidian notes
  - GitHub repo changes/issues
  - user-provided links/repos

intake item:
  - title
  - claim/request
  - source
  - evidence
  - why it matters
  - likely department
  - risk level

rubric:
  - user impact
  - automation leverage
  - feasibility
  - urgency
  - safety/privacy
  - dashboard visibility value

research lanes:
  - verify need
  - inspect current Cosmos state
  - search existing solution/reference
  - implementation estimate

routes:
  - build
  - dashboard
  - docs
  - integration
  - research
  - shelve

human gate:
  - approve <slug>
  - modify <slug>
  - shelve <slug>
```

## Next implementation step

Use the reference repo as a design template, but do not blindly vendor its code into Cosmos yet. First create a Cosmos-specific workflow config and run it against the reference engine. If the shape works, then either:

1. keep the reference repo as an external/submodule-style dependency, or
2. copy only the generic engine pieces into Cosmos under `workflows/engine/`.

For now, Cosmos has a draft config at:

```text
workflows/cosmos-improvement-triage.yaml
```
