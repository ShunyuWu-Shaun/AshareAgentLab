# Paper Trading Loop

This project supports paper trading only. It does not connect to a broker and does not place real orders.

## Objective

Use a 100,000 RMB virtual portfolio to test whether an LLM-native A-share research loop can improve its process over time.

The loop optimizes paper-trading performance subject to:

- A-share lot-size constraints,
- T+1 sell availability,
- price-limit checks,
- estimated transaction costs,
- evidence and timestamp discipline,
- daily reflection before prompt/process changes.

## Daily Process

1. Ingest events.
2. Run the agent committee.
3. Convert watchlist items into paper orders.
4. Apply A-share execution constraints.
5. Mark positions to close.
6. Record P/L, lesson, and prompt adjustment.
7. Review whether the adjustment is an actual process improvement or just overfitting to one day.

## Run

```bash
asharelab paper-day --starting-cash 100000
```

Outputs:

- `data/paper_portfolio.json`
- `data/loop_journal.jsonl`

The command is idempotent by default for a trading day. Use `--allow-repeat`
only when deliberately stress-testing prompt or process variants.

## Loop Engineering Notes

The system should improve prompts only through written evidence:

- If losses come from risk feedback, tighten veto logic.
- If losses come from sizing, change exposure caps.
- If losses come from late entry, change confirmation timing.
- If gains come from one lucky sample, do not increase risk immediately.

The next step is to replace mock quotes with timestamped market snapshots and to add a prompt-version registry.

## Rule References

- Shanghai Stock Exchange trading mechanism: https://english.sse.com.cn/start/trading/mechanism/
- Official 2023 stamp-duty reduction report: https://jingji.cctv.com/2023/08/28/ARTIfrdgrZnN0vsBJFddvOyH230828.shtml
