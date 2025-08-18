import os
import pathlib
from typing import Dict, Any

import pytest
import shutil
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
    data["model1"] = os.getenv("HF_MODEL", data.get("model1"))
    data["model2"] = os.getenv("HF_MODEL", data.get("model2"))
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


ARTIFACTS_DIR = "artifacts"

@pytest.fixture(scope="session", autouse=True)
def prepare_artifacts():
    artifacts_path = pathlib.Path(ARTIFACTS_DIR)
    if artifacts_path.exists():
        shutil.rmtree(artifacts_path)
    artifacts_path.mkdir(parents=True, exist_ok=True)
    return artifacts_path
