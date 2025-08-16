import pathlib
from typing import Dict, Any

import pytest

from tests.reporting import generate_markdown_summary


@pytest.mark.order("last")
def test_generate_markdown_summary(config: Dict[str, Any], artifacts_dir: pathlib.Path, reports_dir: pathlib.Path) -> None:
    md_path = reports_dir / "summary.md"
    generate_markdown_summary(artifacts_dir, md_path)
    assert md_path.exists(), "summary.md should be generated"
