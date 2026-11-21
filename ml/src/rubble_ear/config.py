from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT = ROOT / "ml" / "configs" / "default.yaml"


def load(path: Path | str = DEFAULT) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
