# Bot Factory

Reusable skill for creating new Hermes profiles + Telegram-bound cron bots.

## Trigger
Use when creating a new named profile/bot from scratch.

## Steps
1. Create profile directories:
   - `/opt/data/profiles/<SlugifiedName>/`
   - `/opt/data/.hermes/profiles/<SlugifiedName>/skills/<slugifiedname>/SKILL.md`
   - `/opt/data/.hermes/profiles/<SlugifiedName>/memories/`
   - `/opt/data/.hermes/profiles/<SlugifiedName>/cron/`

2. Write profile SOUL.md at `/opt/data/profiles/<Name>/SOUL.md`

3. Write skill at `/opt/data/.hermes/profiles/<SlugifiedName>/skills/<slugifiedname>/SKILL.md`

4. Register in Hermes:
   - `hermes profile create <SlugifiedName> --path /opt/data/profiles/<SlugifiedName>`

5. Register in `/opt/data/Cosmos/profiles/registry.yaml`:
   - name
   - slug
   - chat target (default: `origin` until renamed)
   - cron jobs
   - created
   - rollback note with commit/branch

6. If any step fails: mark status `failed` with reason so the CEO can safely revert.
