# Cosmos Model Routing

## Default model strategy

Cosmos is model-agnostic. It should use the best available model for each task while respecting budget and privacy.

## Provider roles

- OpenRouter free models: basic scraping, tagging, simple summaries, routine background work.
- OpenRouter cheap paid models: batch processing, moderate summaries, non-sensitive research.
- OpenAI: generalist reasoning, synthesis, planning, polished summaries.
- Claude/Anthropic: deep reasoning, architecture, writing, code understanding.
- Claude Code/Codex/OpenCode: actual implementation and repo work.
- Future local models: private low-risk note processing and offline work.

## Escalation

Start cheap when low-risk. Escalate when:

- output quality is insufficient
- task is complex
- personal context matters
- final decision/review is needed
- coding agent needs stronger reasoning

## Budget awareness

Track provider, model, estimated cost, actual cost, and whether the task could have used a cheaper model.
