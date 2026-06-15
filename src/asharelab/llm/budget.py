from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderPricing:
    provider: str
    model: str
    input_per_million: float
    output_per_million: float
    currency: str = "USD"
    cached_input_per_million: float | None = None


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int = 0


PRICING: dict[str, ProviderPricing] = {
    "deepseek": ProviderPricing(
        provider="deepseek",
        model="deepseek-chat",
        input_per_million=0.14,
        cached_input_per_million=0.0028,
        output_per_million=0.28,
    ),
    "qwen": ProviderPricing(
        provider="qwen",
        model="qwen3.5-flash",
        input_per_million=0.029,
        output_per_million=0.287,
    ),
    "zhipu": ProviderPricing(
        provider="zhipu",
        model="glm-4.7-flashx",
        input_per_million=0.07,
        cached_input_per_million=0.01,
        output_per_million=0.40,
    ),
    "kimi": ProviderPricing(
        provider="kimi",
        model="kimi-k2.6",
        input_per_million=0.95,
        output_per_million=4.00,
    ),
    "baidu": ProviderPricing(
        provider="baidu",
        model="ernie-4.5-turbo-128k",
        input_per_million=0.8,
        output_per_million=3.2,
        currency="CNY",
    ),
}


def estimate_cost_cny(
    provider: str,
    usage: TokenUsage,
    usd_cny: float = 7.2,
    pricing: dict[str, ProviderPricing] | None = None,
) -> float:
    table = pricing or PRICING
    if provider not in table:
        raise KeyError(f"Unknown provider: {provider}")
    price = table[provider]
    cached = min(usage.cached_input_tokens, usage.input_tokens)
    uncached = usage.input_tokens - cached

    cached_rate = price.cached_input_per_million or price.input_per_million
    native_cost = (
        uncached / 1_000_000 * price.input_per_million
        + cached / 1_000_000 * cached_rate
        + usage.output_tokens / 1_000_000 * price.output_per_million
    )
    return native_cost if price.currency == "CNY" else native_cost * usd_cny


class BudgetGuard:
    def __init__(self, provider: str, monthly_cap_cny: float, usd_cny: float = 7.2):
        self.provider = provider
        self.monthly_cap_cny = monthly_cap_cny
        self.usd_cny = usd_cny
        self.spent_cny = 0.0

    def reserve(self, usage: TokenUsage) -> float:
        cost = estimate_cost_cny(self.provider, usage, self.usd_cny)
        if self.spent_cny + cost > self.monthly_cap_cny:
            raise RuntimeError(
                f"Budget exceeded: projected {self.spent_cny + cost:.2f} RMB "
                f"> cap {self.monthly_cap_cny:.2f} RMB"
            )
        self.spent_cny += cost
        return cost

