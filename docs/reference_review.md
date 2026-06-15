# Critical Reference Review

This project borrows architectural ideas from public LLM-native trading work, but avoids copying large code paths. The initial framework is intentionally smaller and A-share oriented.

## AI-Trader

Useful idea: an agent-native environment where agents can register, search, act, and be evaluated in live or paper markets. It is especially relevant because its benchmark explicitly includes A-shares.

What we do differently: AshareAgentLab starts as a local research lab, not a copy-trading or competition platform. The first milestone is auditable market reading and hypothesis generation.

## TradingAgents

Useful idea: role specialization, bull/bear debate, technical/fundamental/sentiment/risk separation.

What we do differently: A-share short-horizon research needs roles for narrative diffusion, retail crowding, limit-up feedback, and regulatory risk. The starter committee therefore uses NarrativeScout, EmotionGauge, HypothesisBuilder, and Skeptic.

## FinMem

Useful idea: layered memory that lets an agent retain important market episodes and adapt its future reasoning.

What we do differently: we use SQLite first, because human inspection and easy repair matter more than elaborate vector memory in the first month.

## RD-Agent(Q)

Useful idea: close the loop from hypothesis to code implementation, validation, and feedback.

What we do differently: we do not begin with factor-model co-optimization. We use RD-Agent(Q)'s verification discipline to make narrative hypotheses testable.

## Alpha-GPT

Useful idea: translate human trading ideas into executable alpha expressions.

What we do differently: the first version translates A-share narratives into observation checklists and event studies, then later into factors.

## Tushare MCP and Skills

Useful idea: expose financial data as LLM-callable tools.

What we do differently: this repository keeps data adapters as plain Python first, so the same code can later be wrapped as MCP tools without locking the core to one agent client.

## Non-goals

- No automatic live order placement.
- No claim that LLM rationales are faithful explanations.
- No backtest result is accepted without timestamps, universe definition, transaction assumptions, and leakage checks.

