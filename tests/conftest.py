import os
import pathlib
from typing import Dict, Any

import pytest
import yaml


PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _ensure_dir(path: pathlib.Path) -> pathlib.Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    config_path = PROJECT_ROOT / "config.yml"
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # env overrides
    data["model"] = os.getenv("HF_MODEL", data.get("model"))
    data["timeout_seconds"] = int(os.getenv("HF_TIMEOUT", data.get("timeout_seconds", 30)))
    data["artifact_dir"] = os.getenv("HF_ARTIFACT_DIR", data.get("artifact_dir", "artifacts"))
    data["report_dir"] = os.getenv("HF_REPORT_DIR", data.get("report_dir", "reports"))
    return data


@pytest.fixture(scope="session")
def artifacts_dir(config: Dict[str, Any]) -> pathlib.Path:
    return _ensure_dir(PROJECT_ROOT / config["artifact_dir"]) 


@pytest.fixture(scope="session")
def reports_dir(config: Dict[str, Any]) -> pathlib.Path:
    return _ensure_dir(PROJECT_ROOT / config["report_dir"])
