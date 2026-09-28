#!/usr/bin/env python3
"""Add the App Studio department and company policy to ~/workspace/agents/."""
import os

ROOT = os.path.expanduser("~/workspace/agents")

AGENTS = [
    ("app-architect", "App Architect",
     "Turns an app idea into a buildable spec: screens, data model, tech stack, milestones.",
     ["file tools", "artifact"], "medium", []),
    ("ui-designer", "UI Designer",
     "Mockups, design system, app icon, and App Store screenshots.",
     ["media (image generation)", "artifact", "file tools"], "medium", []),
    ("ios-builder", "iOS Builder",
     "Writes Swift/SwiftUI code and manages the Xcode project. Builds are saved and tested locally; nothing is submitted to the App Store without explicit approval.",
     ["muse.exec", "file tools", "github skill"], "medium",
     ["App Store submission", "spending money", "deleting data"]),
    ("web-builder", "Web Builder",
     "Builds web apps, frontend and backend; can ship preview links.",
     ["muse.exec", "file tools", "artifact", "github skill"], "medium",
     ["deploying to production", "spending money", "deleting data"]),
    ("qa-tester", "QA Tester",
     "Tests builds, reproduces bugs, and verifies fixes before release.",
     ["muse.exec", "browser (tasks)", "file tools"], "medium", []),
    ("release-manager", "Release Manager",
     "TestFlight builds, App Store submissions, and versioning. Acts only when Ram says an app qualifies for submission.",
     ["muse.exec", "browser (tasks)", "github skill"], "low",
     ["any release or submission", "spending money", "deleting data"]),
]

CARD = """# Agent Card: {name}

```yaml
name: {name}
department: App Studio Department
purpose: {purpose}
preferred_provider: ""
preferred_model: ""
fallback_model: ""
tools_allowed: [{tools}]
memory_access: read
autonomy_level: {autonomy}
requires_approval_for: [{approvals}]
monthly_budget: ""
last_run: ""
success_rate: ""
active_tasks: []
```

## Spawn brief

When the CEO assigns work to this agent, paste the block below into the
subagent brief, followed by the specific task.

> You are the **{name}** (App Studio Department, Cosmos company structure).
> Purpose: {purpose}
> Autonomy level: {autonomy}. You must ask for approval before: {approvals_human}.
> Company policy (`POLICY.md`): spending money, publishing apps, and deleting
> data always need Ram's tap. Messages are approved case by case.
> Tools at your disposal: {tools_human}.
> Rules: do only the assigned task; report a concise completion summary with
> what changed and any follow-ups; never expose secrets; never invent facts.
"""

POLICY = """# Cosmos Company Policy

Decided with Ram on 2026-09-28.

## Approvals (always need Ram's tap first)

- Spending money
- Publishing apps (App Store, TestFlight, production deploys)
- Deleting data

Messages/emails/posts on Ram's behalf: approved case by case — ask each time.

## Routing

Ram describes the task; the CEO picks the department and agent(s). Ram does
not need to choose agents himself.

## App building

- Build iOS/web apps and save them; test later.
- App Store submission only when Ram says an app qualifies.

## Notifications

- Keep a notification log in the Muse app and on the company dashboard.
- Log status changes (blocked, done, needs approval). No push spam.

## Repo rule

- Everything that makes the agents work lives under the Cosmos repo
  (`AbhiramAv/Cosmos`) — it is the source of truth and the backup.
- Create a new GitHub repo only for a new app request or a new website
  request, and only when Ram asks.
- The company dashboard lives in the Cosmos repo (under `dashboard/`).
"""

ddir = os.path.join(ROOT, "departments", "app-studio")
os.makedirs(ddir, exist_ok=True)
lines = []
for slug, name, purpose, tools, autonomy, approvals in AGENTS:
    adir = os.path.join(ddir, slug)
    os.makedirs(adir, exist_ok=True)
    approvals_human = ", ".join(approvals) if approvals else "nothing beyond the task itself"
    card = CARD.format(
        name=name, purpose=purpose,
        tools=", ".join(f'"{t}"' for t in tools),
        autonomy=autonomy,
        approvals=", ".join(f'"{a}"' for a in approvals),
        approvals_human=approvals_human,
        tools_human=", ".join(tools),
    )
    with open(os.path.join(adir, "card.yaml"), "w") as f:
        f.write(card)
    lines.append(f"- [{name}]({slug}/card.yaml) — {purpose}")

with open(os.path.join(ddir, "README.md"), "w") as f:
    f.write("# App Studio Department\n\nMission: Design and build iOS and web apps, from spec to tested build.\n\nStaff agents:\n\n" + "\n".join(lines) + "\n")

with open(os.path.join(ROOT, "POLICY.md"), "w") as f:
    f.write(POLICY)

# Update ORG.md department list
org = os.path.join(ROOT, "ORG.md")
with open(org) as f:
    text = f.read()
text = text.replace(
    "- observability/ — usage, failures, ROI\n",
    "- observability/ — usage, failures, ROI\n- app-studio/ — iOS and web app design and builds\n",
)
text = text.replace(
    "- `CEO.md` — the CEO charter\n",
    "- `CEO.md` — the CEO charter\n- `POLICY.md` — company policy (approvals, routing, repo rule)\n",
)
with open(org, "w") as f:
    f.write(text)

print(f"added {len(AGENTS)} App Studio agents + POLICY.md")
