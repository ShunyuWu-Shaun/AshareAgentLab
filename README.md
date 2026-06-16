# AshareAgentLab

LLM-native A-share research lab for narrative, sentiment, capital-flow clues, and testable hypotheses.

This repository is not a trading bot. It is a local-first research system that helps an LLM/agent team read the A-share market, keep an auditable memory, turn narratives into hypotheses, and ask deterministic code to verify them.

## Why This Shape

Traditional quant stacks start from factors and models. A-share short-horizon opportunities often start from narratives, liquidity, policy signals, retail attention, and risk feedback. AshareAgentLab therefore puts the agent loop first:

1. Perceive: collect market events, limit-up pools, sector moves, money flow, announcements, and public discussion.
2. Remember: store time-stamped events, narrative states, hypotheses, and outcomes.
3. Debate: run role-specific agents for narrative scouting, emotion, hypothesis generation, and skepticism.
4. Verify: convert claims into event studies or backtests before they become watchlist candidates.
5. Report: produce readable daily notes with evidence and invalidation conditions.

## Repository Layout

```text
src/asharelab/
  agents/      role agents and the committee runner
  data/        A-share data source interfaces and adapters
  llm/         OpenAI-compatible client, provider registry, budget guard
  memory/      SQLite market memory
  research/    hypothesis validation and event-study helpers
  reports/     markdown report rendering
configs/       local configuration templates
docs/          architecture, source review, and LLM cost analysis
scripts/       deployment helpers
tests/         focused unit tests
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp configs/example.env .env
asharelab doctor
asharelab demo --offline
asharelab estimate --provider deepseek --input-tokens 20000000 --output-tokens 5000000
asharelab paper-day --starting-cash 100000
```

The offline demo uses deterministic mock data, so it can run before any API key or market-data token is configured.

## DeepSeek API

DeepSeek uses an OpenAI-compatible API. Create your own API key in the DeepSeek platform, then put it in `.env`:

```bash
ASHARELAB_LLM_PROVIDER=deepseek
ASHARELAB_LLM_MODEL=deepseek-v4-flash
ASHARELAB_LLM_API_KEY=sk-...
```

Then run:

```bash
asharelab llm-smoke
```

Codex should not register accounts, bind payment methods, or store API keys in Git.

## Paper Trading Loop

`asharelab paper-day` runs a deterministic offline paper-trading loop with 100,000 RMB virtual capital by default:

1. collect normalized mock A-share events,
2. run the agent committee,
3. apply A-share paper-trading rules,
4. update the paper portfolio,
5. write a loop journal with P/L, lessons, and prompt/process adjustment.

Artifacts are stored under `/data`, which is intentionally ignored by Git.

## Early Provider Recommendation

Use DeepSeek as the default low-cost OpenAI-compatible provider, with Qwen or GLM as fallback models for harder synthesis. Keep the first month under 500 RMB by:

- routing extraction and JSON normalization to cheap models,
- caching repeated context aggressively,
- limiting daily reports to compact evidence snippets,
- running expensive reasoning only on short candidate lists.

See [docs/llm_costs.md](docs/llm_costs.md) for the budget model.

## Safety Boundary

This project is for research, simulation, and decision support. It should not place live orders without a separate execution system, explicit human approval, broker-side risk checks, and a written trading policy.
