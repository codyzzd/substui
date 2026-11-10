from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from platformdirs import user_config_path


@dataclass(slots=True)
class Settings:
    language: str = "pt-BR"
    start_path: str = str(Path.home())


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or user_config_path("substui", appauthor=False) / "settings.json"

    def load(self) -> Settings:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return Settings(
                language=str(data.get("language", "pt-BR")),
                start_path=str(data.get("start_path", Path.home())),
            )
        except (OSError, ValueError, TypeError):
            return Settings()

    def save(self, settings: Settings) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(asdict(settings), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            return False
        return True

