from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from asharelab.config import LlmSettings


PROVIDER_BASE_URLS = {
    "deepseek": "https://api.deepseek.com",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "kimi": "https://api.moonshot.cn/v1",
    "siliconflow": "https://api.siliconflow.cn/v1",
}


@dataclass
class LlmResponse:
    content: str
    usage: dict[str, Any]


class ChatClient:
    """Small OpenAI-compatible wrapper with a mock mode for local development."""

    def __init__(self, settings: LlmSettings):
        self.settings = settings

    def complete(self, system: str, user: str, *, response_format: str = "text") -> LlmResponse:
        if self.settings.provider == "mock":
            return self._mock_complete(user, response_format=response_format)

        if not self.settings.api_key:
            raise RuntimeError("ASHARELAB_LLM_API_KEY is required for non-mock providers")

        from openai import OpenAI

        base_url = self.settings.base_url or PROVIDER_BASE_URLS.get(self.settings.provider)
        if not base_url:
            raise RuntimeError(f"No base URL configured for provider {self.settings.provider}")

        client = OpenAI(api_key=self.settings.api_key, base_url=base_url)
        kwargs: dict[str, Any] = {}
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        completion = client.chat.completions.create(
            model=self.settings.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=self.settings.temperature,
            **kwargs,
        )
        usage = completion.usage.model_dump() if completion.usage else {}
        return LlmResponse(content=completion.choices[0].message.content or "", usage=usage)

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        response = self.complete(system, user, response_format="json")
        try:
            loaded = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Model did not return valid JSON: {response.content[:300]}") from exc
        if not isinstance(loaded, dict):
            raise ValueError("Expected JSON object from model")
        return loaded

    def _mock_complete(self, user: str, *, response_format: str) -> LlmResponse:
        if response_format == "json":
            content = json.dumps(
                {
                    "summary": "Mock agent response for local development.",
                    "signals": ["narrative_heat", "risk_review"],
                    "input_preview": user[:160],
                },
                ensure_ascii=False,
            )
        else:
            content = "Mock agent response for local development."
        return LlmResponse(content=content, usage={"input_tokens": len(user) // 2, "output_tokens": 32})

