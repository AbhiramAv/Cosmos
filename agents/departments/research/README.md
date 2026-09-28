# Research Department

Mission: Handles public information gathering and synthesis.

Staff agents:

- [Quick Researcher](quick-researcher/card.yaml) — Fast searches and lightweight summaries.
- [Scraper Agent](scraper/card.yaml) — Public-page scraping and extraction; prefers cheap/free approaches.
- [Source Validator](source-validator/card.yaml) — Checks source quality and flags contradictions.

Each agent has a directory here with an agent `card.yaml` and a spawn-ready
brief. The CEO (main agent) assigns work by spawning a subagent with the
card's brief plus the specific task.
