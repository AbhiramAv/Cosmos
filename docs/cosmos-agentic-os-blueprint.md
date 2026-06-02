# Cosmos Agentic OS Blueprint

Cosmos is Ram's personal agentic operating system: one CEO/orchestrator agent with a staff of specialist agents, shared memory, visible dashboards, and safe automation.

## North Star

Help Ram live more of his life by turning recurring thinking, admin, research, project, and coding work into supervised agent workflows that execute, log, remember, and improve.

## Core thesis

Cosmos is not a chatbot. Cosmos is an operating layer around Hermes Agent that can:

- receive commands from Telegram and future interfaces
- understand goals and missions
- route tasks to the right model, tool, or sub-agent
- execute safe actions directly
- ask when risk, ambiguity, secrets, or external consequences matter
- save useful artifacts instead of losing them in chat
- maintain memory across Hermes, Obsidian, Supabase, and GitHub
- show what happened through a visual dashboard
- run recurring dream/heartbeat jobs that improve the system while Ram sleeps

## System layers

```text
Ram
  ↓
Telegram / future browser dashboard / Obsidian
  ↓
Cosmos CEO Agent
  ↓
Task Router + Permission Gate + Provider Router
  ↓
Agent Company
  ├── Operations
  ├── Knowledge
  ├── Research
  ├── Engineering
  ├── Life OS
  └── Observability
  ↓
Tools, providers, integrations, cron jobs, subagents
  ↓
Memory + logs + artifacts
  ├── Hermes memory/session search/skills
  ├── Obsidian second brain
  ├── Supabase machine-readable backend
  └── GitHub versioned source of truth
  ↓
Visual Intelligence Dashboard
```

## MVP v1

The first version should focus on structure and observability before heavy automation.

1. Define the CEO agent, departments, staff agents, and routing policies.
2. Create a Mission Control model for goals that span days or weeks.
3. Create a dashboard specification with agent staff map, task queue, usage, cron registry, memory, and artifacts.
4. Create an Obsidian structure for human-readable second brain records.
5. Draft Supabase schema for structured tasks, runs, artifacts, usage, and memory.
6. Establish permissions and least-access rules.
7. Add recurring dream/morning/usage review job designs.
8. Keep secrets out of GitHub, Obsidian, chat logs, and sub-agent prompts.

## Principles

- Cosmos acts first for safe, generic work.
- Cosmos asks before destructive, external, expensive, sensitive, or ambiguous work.
- The CEO agent owns task routing and final review.
- Sub-agents receive only the context and tools they need.
- Obsidian is the readable second brain.
- Supabase is the structured backend when useful.
- GitHub stores versioned docs, configs, prompts, templates, and dashboard code.
- Every meaningful artifact should be saved, searchable, and linked to a task or mission.
- Cheap/free models handle low-risk routine work.
- Premium models handle reasoning, synthesis, personal context, and final review.
- Nightly dream reviews compound progress without requiring willpower.

## Open decisions

- Exact Obsidian vault path and sync mechanism.
- Whether Supabase v1 uses an existing project or a new Cosmos-specific project.
- First dashboard stack: Obsidian-first, local web dashboard, or both.
- Which provider keys are already configured and which should be Cosmos-specific.
- Which integrations should be enabled first: email, calendar, GitHub, Supabase, Obsidian, browser, or meeting notes.
