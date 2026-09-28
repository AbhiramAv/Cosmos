# Life OS Department

Mission: Supports personal systems.

Staff agents:

- [Habit/Routine Agent](habit-routine/card.yaml) — Routines, check-ins, and habit logs.
- [Reflection Agent](reflection/card.yaml) — Journaling prompts and personal insights.
- [Goal Tracker](goal-tracker/card.yaml) — Maps life and project goals into Mission Control.

Each agent has a directory here with an agent `card.yaml` and a spawn-ready
brief. The CEO (main agent) assigns work by spawning a subagent with the
card's brief plus the specific task.
