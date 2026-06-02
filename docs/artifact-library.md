# Artifact Library

Agents often create useful artifacts that get lost in chat. Cosmos should save, index, and display them.

## Artifact types

- markdown plans
- research reports
- HTML pages
- invoices
- documents
- images
- diagrams
- code snippets
- dashboards
- summaries
- generated templates

## Storage proposal

```text
artifacts/
  documents/
  reports/
  html/
  markdown/
  images/
  diagrams/
  generated/
  metadata/
```

## Metadata schema

```yaml
id:
title:
five_word_summary:
description_13_words:
type:
path:
created_at:
created_by_agent:
source_session:
related_task:
related_mission:
tags:
sensitivity:
sync_to_obsidian:
sync_to_github:
```

## Dashboard features

- search
- filter by type
- preview
- open file
- link to mission/task
- see creating agent
- delete with confirmation
- sync to Obsidian/GitHub when appropriate

## Rule

If Cosmos creates something Ram may want later, save it as an artifact and link it to a task or mission.
