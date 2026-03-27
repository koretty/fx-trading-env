from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings for viewer startup."""

    csv_path: Path
    window_size: int = 120
    initial_step: int = 120


class ConfigLoader:
    """Loads runtime configuration from YAML/JSON and CLI override values."""

    @staticmethod
    def load(
        config_path: str | Path | None = None,
        csv_path_override: str | Path | None = None,
        window_size_override: int | None = None,
        initial_step_override: int | None = None,
    ) -> AppConfig:
        raw: dict[str, Any] = {}
        config_file_path: Path | None = None

        if config_path is not None:
            conf = Path(config_path)
            if not conf.exists():
                raise FileNotFoundError(f"Config file not found: {conf}")
            config_file_path = conf.resolve()
            raw = ConfigLoader._load_config_file(config_file_path)

        base_dir = Path(__file__).resolve().parents[2]
        csv_path = (
            ConfigLoader._resolve_cli_csv_path(Path(csv_path_override), base_dir)
            if csv_path_override
            else ConfigLoader._resolve_csv_path(raw, base_dir, config_file_path)
        )

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
    def _load_config_file(config_file_path: Path) -> dict[str, Any]:
        suffix = config_file_path.suffix.lower()

        if suffix == ".json":
            with config_file_path.open("r", encoding="utf-8") as fp:
                raw = json.load(fp)
        elif suffix in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore[reportMissingImports]
            except ModuleNotFoundError as exc:
                raise ModuleNotFoundError(
                    "YAML config requires PyYAML. Install with: pip install pyyaml"
                ) from exc

            with config_file_path.open("r", encoding="utf-8") as fp:
                loaded = yaml.safe_load(fp)
            raw = {} if loaded is None else loaded
        else:
            raise ValueError(
                f"Unsupported config format: {config_file_path.suffix}. "
                "Use .json, .yaml, or .yml"
            )

        if not isinstance(raw, dict):
            raise ValueError("Config root must be a mapping/object")

        return raw

    @staticmethod
    def _resolve_cli_csv_path(raw_path: Path, base_dir: Path) -> Path:
        if raw_path.is_absolute():
            return raw_path
        return (base_dir / raw_path).resolve()

    @staticmethod
    def _resolve_csv_path(raw: dict[str, Any], base_dir: Path, config_file_path: Path | None) -> Path:
        raw_csv = raw.get("csv_path")
        if raw_csv:
            csv_path = Path(str(raw_csv))
            if csv_path.is_absolute():
                return csv_path

            if config_file_path is not None:
                return (config_file_path.parent / csv_path).resolve()

            return (base_dir / csv_path).resolve()

        csv_candidates = sorted((base_dir / "src").glob("*.csv"))
        if not csv_candidates:
            raise FileNotFoundError("No CSV found under src/. Specify --csv or config csv_path.")
        return csv_candidates[0]
