# Cron Registry

Cron jobs and heartbeats make Cosmos feel alive. They must be visible, auditable, and easy to pause.

## Initial jobs

### Nightly Dream Agent

Reviews recent activity and generates insights.

### Daily Morning Brief

Delivers a concise summary and next actions to Ram.

### Weekly AI Usage Review

Analyzes provider/model spend, waste, and routing improvements.

### Weekly Agent Performance Review

Checks agent success rates, failures, and suggested improvements.

### Nightly GitHub Sync

Keeps Cosmos repo synced. Existing job currently handles nightly GitHub sync logic.

### Obsidian Sync Check

Verifies Obsidian structure and sync health once vault path is known.

### Failed Job Watchdog

Detects stuck, failed, or repeatedly failing jobs.

### Memory Cleanup Review

Suggests memory consolidation and stale context cleanup.

## Cron job record

```yaml
name:
schedule:
status: enabled | paused | failed
owner_agent:
last_run:
next_run:
last_output_summary:
failure_count:
delivery_target:
related_dashboard_panel:
```

## Dashboard requirements

- show every job in one place
- show last/next run
- show failure count
- show output summary
- allow pause/resume/remove with appropriate confirmation
