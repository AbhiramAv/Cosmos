# Cosmos Company — Agent Structure

Source of truth for the org chart: `AbhiramAv/Cosmos`
(`docs/agent-company-structure.md`, `assistant/soul.md`).
This directory is the working copy the CEO (the main agent, acting as CEO)
uses day to day.

## How it works

- The CEO receives Ram's requests, breaks them into tasks, and assigns work
  to departments or individual staff agents.
- A staff agent is run by spawning a subagent (`subagent.spawn`) with that
  agent's spawn brief (see its `card.yaml`) plus the specific task.
- CEO duties: clarify only when ambiguity changes the action, choose
  tools/providers, enforce permission rules, review outputs, update memory /
  logs / artifacts / dashboards, and report concise completion results.
- Safety: never store raw secrets in cards or logs; subagents don't get raw
  secrets by default; ask before destructive, external, expensive, sensitive,
  or irreversible actions.

## Departments

- operations/ — daily execution and admin
- knowledge/ — memory and notes
- research/ — public information gathering and synthesis
- engineering/ — code, GitHub, Supabase, dashboard, automation
- life-os/ — personal systems
- observability/ — usage, failures, ROI
- app-studio/ — iOS and web app design and builds

## Files

- `CEO.md` — the CEO charter
- `POLICY.md` — company policy (approvals, routing, repo rule)
- `departments/<dept>/README.md` — department brief
- `departments/<dept>/<agent>/card.yaml` — agent card + spawn brief
