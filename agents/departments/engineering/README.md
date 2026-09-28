# Engineering Department

Mission: Handles code, GitHub, Supabase, dashboard, and automation.

Staff agents:

- [Coding Agent](coding/card.yaml) — Implements repo changes, scripts, and small tools.
- [Debugging Agent](debugging/card.yaml) — Investigates failures systematically and proposes fixes.
- [GitHub Manager](github-manager/card.yaml) — Issues, branches, PRs, sync, and repo hygiene.
- [Supabase Agent](supabase/card.yaml) — Schema, migrations, backend queries, and data checks.

Each agent has a directory here with an agent `card.yaml` and a spawn-ready
brief. The CEO (main agent) assigns work by spawning a subagent with the
card's brief plus the specific task.
