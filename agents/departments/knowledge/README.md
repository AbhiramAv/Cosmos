# Knowledge Department

Mission: Manages memory and notes.

Staff agents:

- [Obsidian Librarian](obsidian-librarian/card.yaml) — Organizes notes, dashboards, and second-brain structure.
- [Memory Curator](memory-curator/card.yaml) — Proposes durable memories and cleans stale context.
- [Daily Log Agent](daily-log/card.yaml) — Writes daily summaries, check-ins, and activity logs.

Each agent has a directory here with an agent `card.yaml` and a spawn-ready
brief. The CEO (main agent) assigns work by spawning a subagent with the
card's brief plus the specific task.
