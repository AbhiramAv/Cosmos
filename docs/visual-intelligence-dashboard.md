# Visual Intelligence Dashboard

The dashboard makes invisible agent work visible. It is the visual layer around Hermes/Cosmos, not a replacement for Telegram.

## Dashboard modules

### 1. Command Center

- chat with Cosmos CEO
- see current active mission
- quick actions: queue task, run background task, stop task, set goal, switch mode

### 2. CEO Status

- current model/provider
- active session
- memory status
- tool availability
- last action
- blocked decisions requiring Ram

### 3. Agent Staff / Pantheon

- visual hierarchy of CEO, departments, and staff agents
- agent cards with status, model, monthly usage, permissions, and last run

### 4. Mission Control

- active mid-term goals
- progress bars
- Ram-owned actions
- Cosmos-owned actions
- blocked items
- related tasks/artifacts/notes

### 5. Task Queue

- queued
- running
- background
- waiting on Ram
- failed
- completed

### 6. Artifact Library

- generated documents, markdown, reports, HTML, images, decks, invoices, and plans
- search, filter, preview, open, delete with confirmation

### 7. Dream Insights

- nightly dream brief
- morning brief
- weak signals
- suggested automations
- cost warnings
- project/life insights

### 8. Memory Browser

- Hermes memory summaries
- Obsidian memory notes
- Supabase memory records
- recent memory changes
- source visibility

### 9. Usage and Cost

- provider usage by month
- model usage by agent
- OpenAI/Claude/OpenRouter spend
- free-model job count
- most expensive mission/task
- savings recommendations

### 10. Cron Registry

- all scheduled jobs
- schedule
- last run
- next run
- output
- failure count
- enabled/paused status

### 11. Integration Status

- Telegram
- GitHub
- Obsidian
- Supabase
- provider keys/auth
- MCP servers
- browser/computer tools

### 12. Conversation History

- recent sessions
- searchable summaries
- links to artifacts and missions

## MVP dashboard order

1. Obsidian-first dashboard markdown.
2. Static/local web dashboard mockup.
3. Live dashboard backed by Supabase/Hermes data.
4. Hosted dashboard if Ram wants phone/browser access anywhere.
