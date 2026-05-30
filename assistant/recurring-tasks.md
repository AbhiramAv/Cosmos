# Recurring Tasks

Use this file for reminders, scheduled check-ins, and automations Ram wants Cosmos to run.

## Active automations

- Cosmos nightly GitHub sync: scheduled via Hermes cron watchdog, runs hourly but only performs sync once during `00:00-00:59 America/New_York`.
  - Script: `/opt/data/scripts/cosmos-nightly-sync.sh`
  - Cron job: `7580b716a6dc`
  - Purpose: commit and push `/opt/data/Cosmos` to `origin/main` as the source of truth.

## Ideas

- Daily planning check-in
- Evening review
- Health/sick-day check-ins
- Weekly goals review
