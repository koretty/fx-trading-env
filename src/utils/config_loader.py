from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings for viewer startup."""

    csv_path: Path
    window_size: int = 120
    initial_step: int = 120


class ConfigLoader:
    """Loads configuration from JSON and CLI fallback values."""

    @staticmethod
    def load(
        config_path: str | Path | None = None,
        csv_path_override: str | Path | None = None,
        window_size_override: int | None = None,
        initial_step_override: int | None = None,
    ) -> AppConfig:
        raw: dict[str, object] = {}

        if config_path is not None:
            conf = Path(config_path)
            if not conf.exists():
                raise FileNotFoundError(f"Config file not found: {conf}")
            with conf.open("r", encoding="utf-8") as fp:
                raw = json.load(fp)

        base_dir = Path(__file__).resolve().parents[2]
        csv_path = Path(csv_path_override) if csv_path_override else ConfigLoader._resolve_csv_path(raw, base_dir)

        window_size = (
            int(window_size_override)
            if window_size_override is not None
            else int(raw.get("window_size", 120))
        )
        initial_step = (
            int(initial_step_override)
            if initial_step_override is not None
            else int(raw.get("initial_step", window_size))
        )

        if window_size <= 0:
            raise ValueError("window_size must be > 0")
        if initial_step < 0:
            raise ValueError("initial_step must be >= 0")

        return AppConfig(csv_path=csv_path, window_size=window_size, initial_step=initial_step)

    @staticmethod
    def _resolve_csv_path(raw: dict[str, object], base_dir: Path) -> Path:
        raw_csv = raw.get("csv_path")
        if raw_csv:
            return Path(str(raw_csv))

        csv_candidates = sorted((base_dir / "src").glob("*.csv"))
        if not csv_candidates:
            raise FileNotFoundError("No CSV found under src/. Specify --csv or config csv_path.")
        return csv_candidates[0]
