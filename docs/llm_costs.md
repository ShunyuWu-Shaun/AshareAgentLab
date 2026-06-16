# LLM API Cost Plan

Goal: keep early monthly API spend under 500 RMB while building an A-share narrative and hypothesis system.

## Provider Snapshot

Prices change often. Check provider pages before production use.

| Provider | Starter model | Why consider it | Approx starter price basis |
|---|---|---|---|
| DeepSeek | `deepseek-v4-flash` | Very low cost, OpenAI-compatible, good default for extraction and reports | Official DeepSeek pricing lists low per-million-token input/output prices and cache-hit discounts |
| Alibaba Qwen | `qwen3.5-flash` or current flash model | Strong Chinese language and tool ecosystem, cheap flash tier | Alibaba Model Studio shows low flash-tier prices |
| Zhipu / Z.ai | `glm-4.7-flashx` or current flash model | Agent/coding focus, cheap flash tier | Z.ai pricing page lists low flash model prices |
| Moonshot Kimi | Kimi K-series | Strong long-context reading | More expensive than DeepSeek/Qwen for high-output workflows |
| Baidu Qianfan | ERNIE turbo models | Domestic cloud integration | Competitive, but not the cheapest default |

## Recommendation

Use a router:

1. `deepseek` for extraction, JSON normalization, daily summaries, and hypothesis drafts.
2. `qwen` or `zhipu` as fallback for difficult Chinese reasoning or tool-calling checks.
3. `kimi` only for long-context document review when retrieval cannot shrink the context.

## First-Month Budget

Assume:

- 20 trading days per month
- 30 daily candidate reports
- average 20M input tokens and 5M output tokens monthly for early experiments

With DeepSeek-style pricing, this is comfortably below 500 RMB. The real cost risk is not the model price; it is uncontrolled agent loops. The code therefore includes:

- budget estimation with `asharelab estimate`,
- provider-level routing,
- mock mode for development,
- short evidence snippets instead of full-page context.

## Operational Rules

- Every agent run should log input and output token estimates.
- Long context should pass through retrieval or summarization before reasoning.
- No autonomous retry loops without a max-steps setting.
- Expensive models need an explicit reason in the run log.

## Source Links

- DeepSeek API quick start and OpenAI-compatible format: https://api-docs.deepseek.com/
- DeepSeek model and pricing page: https://api-docs.deepseek.com/quick_start/pricing
- DeepSeek API key authentication: https://api-docs.deepseek.com/api/deepseek-api
