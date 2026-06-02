# Memory Architecture

Cosmos needs multiple memory layers because different facts need different storage.

## Memory layers

### Hermes persistent memory

Use for compact stable facts that should affect future sessions automatically:

- Ram's preferences
- stable environment facts
- durable conventions
- recurring corrections

Do not use for task progress, PR numbers, transient logs, secrets, or artifacts.

### Hermes session search

Use to retrieve past conversations and decisions when Ram refers to previous work.

### Skills

Use for reusable procedures and workflows, especially after complex tasks or repeated patterns.

### Obsidian

Human-readable second brain:

- daily logs
- mission notes
- dream briefs
- memory summaries
- agent activity summaries
- project context
- decision logs

### Supabase

Machine-readable backend:

- tasks
- agent runs
- artifacts metadata
- provider usage
- cron jobs
- structured memory records
- embeddings/vector search when useful

### GitHub / Cosmos repo

Versioned source of truth:

- architecture docs
- prompts
- policies
- dashboard code
- templates
- schema definitions
- non-secret config

## Data classification

```text
Public/low sensitivity → free/cheap models allowed.
Personal but non-sensitive → premium models or local tools, as appropriate.
Sensitive/private → ask before external model use; prefer local/private processing.
Secrets/API keys/passwords → never in model context, Obsidian, or GitHub.
```

## Rule

Agents request capabilities, not secrets.

Example: Scraper Agent asks CEO to run an OpenRouter job; it does not receive the OpenRouter API key.
