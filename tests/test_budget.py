from asharelab.llm.budget import TokenUsage, estimate_cost_cny


def test_deepseek_budget_is_small_for_starter_volume():
    cost = estimate_cost_cny("deepseek", TokenUsage(input_tokens=20_000_000, output_tokens=5_000_000))
    assert cost < 100


def test_cached_input_reduces_cost():
    raw = estimate_cost_cny("deepseek", TokenUsage(input_tokens=10_000_000, output_tokens=1_000_000))
    cached = estimate_cost_cny(
        "deepseek",
        TokenUsage(input_tokens=10_000_000, cached_input_tokens=8_000_000, output_tokens=1_000_000),
    )
    assert cached < raw

