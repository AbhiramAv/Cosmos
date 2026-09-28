# Observability Department

Mission: Tracks usage, failures, and ROI.

Staff agents:

- [Usage Tracker](usage-tracker/card.yaml) — Provider/model cost and token usage reporting.
- [Cost Optimizer](cost-optimizer/card.yaml) — Recommends cheaper routing or subscription changes.
- [Failure Monitor](failure-monitor/card.yaml) — Detects failed jobs, retries, and blocked tasks.

Each agent has a directory here with an agent `card.yaml` and a spawn-ready
brief. The CEO (main agent) assigns work by spawning a subagent with the
card's brief plus the specific task.
