from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class LlmSettings:
    provider: str = "mock"
    model: str = "mock-reasoner"
    api_key: str = ""
    base_url: str = ""
    monthly_budget_cny: float = 500.0
    temperature: float = 0.2


@dataclass(frozen=True)
class MemorySettings:
    sqlite_path: Path = Path("data/market_memory.sqlite")


@dataclass(frozen=True)
class DataSettings:
    default_source: str = "mock"
    cache_dir: Path = Path("data/cache")


@dataclass(frozen=True)
class AppSettings:
    root: Path
    llm: LlmSettings
    memory: MemorySettings
    data: DataSettings


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        loaded = yaml.safe_load(fh) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping config in {path}")
    return loaded


def load_settings(root: Path | None = None) -> AppSettings:
    root = root or Path.cwd()
    load_dotenv(root / ".env")
    config = _read_yaml(root / "configs" / "default.yaml")

    llm_config = config.get("llm", {})
    memory_config = config.get("memory", {})
    data_config = config.get("data", {})

    provider = os.getenv("ASHARELAB_LLM_PROVIDER", llm_config.get("provider", "mock"))
    model = os.getenv("ASHARELAB_LLM_MODEL", llm_config.get("model", "mock-reasoner"))
    budget = float(os.getenv("ASHARELAB_MONTHLY_BUDGET_CNY", llm_config.get("monthly_budget_cny", 500)))

    return AppSettings(
        root=root,
        llm=LlmSettings(
            provider=provider,
            model=model,
            api_key=os.getenv("ASHARELAB_LLM_API_KEY", ""),
            base_url=os.getenv("ASHARELAB_LLM_BASE_URL", llm_config.get("base_url", "")),
            monthly_budget_cny=budget,
            temperature=float(llm_config.get("temperature", 0.2)),
        ),
        memory=MemorySettings(sqlite_path=root / memory_config.get("sqlite_path", "data/market_memory.sqlite")),
        data=DataSettings(
            default_source=data_config.get("default_source", "mock"),
            cache_dir=root / data_config.get("cache_dir", "data/cache"),
        ),
    )

