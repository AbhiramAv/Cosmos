# Operations Department

Mission: Runs daily execution and admin.

Staff agents:

- [Task Manager Agent](task-manager/card.yaml) — Creates, updates, and tracks tasks across the system.
- [Cron Manager Agent](cron-manager/card.yaml) — Registers and monitors recurring jobs; keeps schedules healthy.
- [Admin Assistant Agent](admin-assistant/card.yaml) — Handles routine admin, reminders, and follow-ups.

Each agent has a directory here with an agent `card.yaml` and a spawn-ready
brief. The CEO (main agent) assigns work by spawning a subagent with the
card's brief plus the specific task.
