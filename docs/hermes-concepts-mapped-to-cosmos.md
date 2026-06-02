# Hermes Concepts Mapped to Cosmos

This document maps Jack Roberts' Hermes tutorial concepts into the Cosmos design.

## Agent, not chatbot

Cosmos should perform actions: create files, update notes, create tasks, run research, launch subagents, schedule jobs, and report results.

## Personal assistant, not contractor

Cosmos CEO is Ram's long-term assistant. Claude Code, Codex, OpenCode, and other agents are contractors for specific jobs.

## One brain, many mouths

Cosmos should be accessible through Telegram now and later through a browser dashboard, Obsidian, CLI, or other messaging platforms.

## Local/VPS hosting

Current foundation is the Hermes instance running on this Linux environment with Telegram connected and the Cosmos repo at `/opt/data/Cosmos`. Future hosting can move to a VPS or local machine if needed.

## OAuth vs API keys

OAuth is login-based. API keys are secrets. Secrets must live in `.env`, Hermes auth/config, or a secret manager — not GitHub, Obsidian, or chat logs.

## Model selection

Cosmos should be model-agnostic and route each job by cost, sensitivity, and difficulty.

## Local models

Future private/local workers can process sensitive low-risk notes without external providers.

## Memory

Cosmos combines Hermes persistent memory, session search, Obsidian notes, Supabase records, GitHub docs, and reusable skills.

## soul.md / character bible

Cosmos needs a CEO soul/operating file defining tone, mission, permissions, routing, and privacy boundaries.

## Integrations

Integrations should be added by permission level: low-risk first, then read-only personal data, then write actions, then high-risk actions only with approval.

## MCPs

Prefer MCP/tool integrations over handing raw APIs to agents. Agents should request capabilities, not secrets.

## Skills

Skills are Cosmos muscle memory: reusable procedures for recurring workflows.

## Slash commands

Dashboard equivalents should exist for queue, background, steer, stop, goal, model, active agents, compression, and cron.

## Security

Use principle of least access. Subagents should receive the minimum context/tools needed.

## North Star / goals

Hermes `/goal` maps to Cosmos Mission Control for mid-term outcomes.

## Subagents

Use parallel subagents as worker teams for research, coding, debugging, review, and analysis.

## Heartbeat / cron jobs

Cron jobs become the automation nervous system: dream reviews, morning briefs, usage reviews, watchdogs, and sync jobs.

## Token and cost budget

Use cheap models for routine work, compress long contexts, and avoid overloading every task with every memory/source.

## Operating system, not app

Cosmos is the everything layer for Ram's agentic work: command center, memory, goals, staff, tools, automations, dashboard, and artifacts.

## Shared memory with coding agents

Coding agents should read structured project docs and write results back to GitHub/Obsidian/Supabase so they do not start from zero.
