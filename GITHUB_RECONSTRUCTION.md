# Cosmos Reconstruction Guide

This repo is the single source of truth for the Cosmos + BullBearian setup.
With this file and the committed configs, the entire system can be rebuilt
even if the local machine is lost.

## Repo Metadata
- Remote: https://github.com/AbhiramAv/Cosmos.git
- Primary branch: main
- Maintainer: Abhiram
- Git identity: Hermes <hermes@cosmos.local>

## Rebuild Order
1. Clone this repo
2. Create Hermes profiles
3. Recreate cron jobs
4. Rebuild artifacts the jobs depend on
5. Re-run any one-off scripts to seed data

## Profiles
Profile path: `/opt/data/.hermes/profiles/<name>` or `/opt/data/profiles/<name>`
Current profiles:
- default
- bullbearian

Profile files:
- `SOUL.md`
- `skills/<slug>/SKILL.md`
- `memories/`
- `cron/`
- `plugins/`

### bullbearian profile
- Finance profile for stocks, crypto, frontier tech
- Profile entry created with: `hermes profile create bullbearian`
- Finance skill copied to profile: `custom_skills/bullbearian/SKILL.md`
- Workspace: `/opt/data/Cosmos/finance`

## Cron Contracts
All jobs are deliver-to-origin for BullBearian unless stated otherwise.

### Cosmos Dashboard Collector
- Schedule: `*/15 * * * *`
- Script: `cosmos-dashboard-collector.py`
- Symlink required in cron scripts dir:
  - `~/.hermes/scripts/cosmos-dashboard-collector.py`
  - `~/.hermes/scripts/cosmos-dashboard-watchdog.sh`
- Dashboard server: `node node_modules/vite/bin/vite.js build --outDir dist --emptyOutDir`
- Static server: port 8787 at `http://127.0.0.1:8787`

### Cosmos Nightly GitHub Sync
- Schedule: `0 0 * * *`
- Script: `cosmos-dashboard-watchdog.sh`
- Profile: default
- Delivery: local

### BullBearian Daily Finance Scan
- Schedule: `0 13 * * *` UTC = daily 8 AM EST
- Profile: bullbearian
- Skill: `bullbearian`
- Prompt: holdings summary + $5–$10 opportunity scan with ~$1k budget
- Tools: terminal, file, web

### BullBearian Risk/Alert Scan
- Schedule: `0 15,17,19,21 * * *` UTC = 10 AM, 12 PM, 2 PM, 4 PM EST
- Profile: bullbearian
- Skill: `bullbearian`
- Prompt: scan `risk_watch` symbols + keywords
- Behavior: silent when nothing actionable

### BullBearian Weekly Portfolio Health Check
- Schedule: `0 15 * * 0` UTC = Sunday 10 AM EST
- Profile: bullbearian
- Skill: `bullbearian`
- Prompt: concentration, themes, thesis drift, DCA

### BullBearian Saturday Frontier-Tech Watchlist Builder
- Schedule: `0 17 * * 6` UTC = Saturday 12 PM EST
- Profile: bullbearian
- Skill: `bullbearian`
- Prompt: space/AI/semiconductors/defense/robotics/quantum/miners moonshots $5–$10

## Symlink Requirement
Hermes resolves cron script paths relative to the profile scripts directory.
Create these if rebuilding:
- `/opt/data/.hermes/scripts/cosmos-dashboard-collector.py`
- `/opt/data/.hermes/scripts/cosmos-dashboard-watchdog.sh`

## Hermes Setup Notes
- Wrapper venv bug: wrapper needs `/opt/hermes` on sys.path
- Fixed venv entrypoint exists in `/opt/hermes/.venv`
- Profile creation: `hermes profile create <name>`

## Git Contacts
- Origin: https://github.com/AbhiramAv/Cosmos.git
- Known commit sequence:
  - `94e120d` fix: stabilize dashboard rendering and add command mode
  - `bbf0e20` feat: make dashboard operational and data-driven
  - `6bd344` Enhance Cosmos dashboard telemetry
  - `42a341f` Add session timing and Codex reset telemetry
  - `48f6c0b` chore: nightly Cosmos sync 2026-06-03
  - `d052b47` feat: add dedicated specialist agent registry for cron workflows
  - `5264a82` feat: add price tracker cron workflow and agent registry
  - `4940da1` feat: track HGLRC Rekon35 V2 FPV Drone Analog 2S at $299.99
  - `aee5124` chore: sync BullBearian profile, finance holdings, and 4 cron jobs; remove legacy price tracker

## Finance Data
- Config: `/opt/data/Cosmos/finance/config.json`
- Price helper: `/opt/data/Cosmos/finance/price-quotes.py`
- Sources:
  - Yahoo Finance public pages
  - Google Finance pages
  - CoinGecko when available
- Holdings source of truth: Finance config + user-provided portfolio images

## Known Issues to Rebuild Correctly
- CoinGecko may 429 from this environment; expect Yahoo/Google as primary
- Browser-based quote pages parse JSON-LD; plain regex often fails
- Polar/browser vision is required for verified holdings extraction from tables/images
