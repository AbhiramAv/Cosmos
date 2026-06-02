# Supabase Schema Draft

Supabase should be the machine-readable backend for Cosmos when v1 moves beyond docs.

## Tables

### departments

```sql
id uuid primary key default gen_random_uuid(),
name text not null,
description text,
created_at timestamptz default now()
```

### agents

```sql
id uuid primary key default gen_random_uuid(),
department_id uuid references departments(id),
name text not null,
purpose text,
preferred_provider text,
preferred_model text,
fallback_model text,
autonomy_level int,
monthly_budget numeric,
status text default 'available',
created_at timestamptz default now()
```

### missions

```sql
id uuid primary key default gen_random_uuid(),
title text not null,
status text default 'active',
why_it_matters text,
target_outcome text,
deadline timestamptz,
created_at timestamptz default now(),
updated_at timestamptz default now()
```

### tasks

```sql
id uuid primary key default gen_random_uuid(),
mission_id uuid references missions(id),
assigned_agent_id uuid references agents(id),
title text not null,
status text default 'queued',
priority int default 3,
requires_ram boolean default false,
created_at timestamptz default now(),
updated_at timestamptz default now()
```

### task_runs

```sql
id uuid primary key default gen_random_uuid(),
task_id uuid references tasks(id),
agent_id uuid references agents(id),
provider text,
model text,
status text,
started_at timestamptz,
finished_at timestamptz,
output_summary text,
error text
```

### artifacts

```sql
id uuid primary key default gen_random_uuid(),
task_id uuid references tasks(id),
mission_id uuid references missions(id),
created_by_agent_id uuid references agents(id),
title text not null,
five_word_summary text,
description text,
type text,
path text,
tags text[],
sensitivity text default 'low',
created_at timestamptz default now()
```

### provider_usage

```sql
id uuid primary key default gen_random_uuid(),
agent_id uuid references agents(id),
task_run_id uuid references task_runs(id),
provider text,
model text,
input_tokens bigint,
output_tokens bigint,
cost numeric,
created_at timestamptz default now()
```

### cron_jobs

```sql
id uuid primary key default gen_random_uuid(),
name text not null,
schedule text,
status text,
owner_agent_id uuid references agents(id),
last_run timestamptz,
next_run timestamptz,
failure_count int default 0,
last_output_summary text
```

### memory_items

```sql
id uuid primary key default gen_random_uuid(),
source text,
content text not null,
sensitivity text default 'normal',
created_by_agent_id uuid references agents(id),
created_at timestamptz default now(),
updated_at timestamptz default now()
```

### dream_briefs

```sql
id uuid primary key default gen_random_uuid(),
period_start timestamptz,
period_end timestamptz,
summary text,
recommendations jsonb,
created_at timestamptz default now()
```

## Future tables

- integrations
- permissions
- routing_rules
- artifact_previews
- memory_embeddings
- conversation_summaries
