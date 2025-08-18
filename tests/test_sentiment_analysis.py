import json
import hashlib
import pathlib
import shutil
import re
import random
from typing import Dict, Any, List, Tuple

import pytest
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

from huggingface_hub import InferenceClient
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from tests.conftest import artifacts_dir, reports_dir
from tests.generate_markdown_report_sa import generate_markdown_summary_sa


def load_test_inputs() -> List[Tuple[str, str]]:
    """Load test inputs from CSV file (sentence, sentiment)."""
    test_data_path = pathlib.Path(__file__).parent.parent / "test_data" / "sentiment _analysis.csv"

    if not test_data_path.exists():
        # fallback to small hardcoded dataset
        print("Using fallback dataset")
        return [
            ("I love this movie!", "positive"),
            ("This is the worst experience ever.", "negative"),
            ("It was okay, nothing special.", "neutral"),
        ]

    if test_data_path.is_file():
        try:
            df = pd.read_csv(test_data_path)
        except Exception as e:
            print(f"Failed to read CSV: {e}, falling back to default dataset")
            df = None

        if df is not None:
            # Ensure required columns
            if not {"Sentence", "Sentiment"}.issubset(df.columns):
                raise ValueError("CSV must have columns: sentence, sentiment")
            # Pick a random sample of 3 rows
            sample = df.sample(min(3, len(df)))
            return list(zip(sample["Sentence"].tolist(), sample["Sentiment"].tolist()))


@pytest.mark.parametrize("row", load_test_inputs(), ids=lambda v: "Sent_" + re.sub(r'[^a-zA-Z0-9_]', '_', v[0][:15]))
def test_sentiment_analysis(config: Dict[str, Any], artifacts_dir: pathlib.Path, row: Tuple[str, str]) -> None:
    sentence, true_label = row

    # Load env
    env_path = pathlib.Path(".env")
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    token = os.getenv("HF_TOKEN")
    if token:
        token = token.strip()
    if not token or token == "***":
        pytest.skip("HF_TOKEN not set or is placeholder, skipping test")

    # Inference client
    client = InferenceClient(
        token=token,
        timeout=config.get("timeout_seconds", 30),
        provider=config.get("provider", "hf-inference"),
    )

    # Call sentiment-analysis
    #result = client.text_classification(model=config["model2"], inputs=sentence)
    result = client.text_classification(
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    text=sentence)

    pred_label = result[0]["label"].lower() if isinstance(result, list) and result else "unknown"

    # Compute per-sample metrics
    y_true = [true_label.lower()]
    y_pred = [pred_label]
    accuracy = int(y_true[0] == y_pred[0])  # 1 if correct, 0 if not
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=[true_label.lower()], average="weighted", zero_division=0
    )

    evaluation = {
        "accuracy": accuracy,
        "precision": prec,
        "recall": rec,
        "f1": f1
    }

    save_api_test_result(config, sentence, true_label, pred_label, evaluation, artifacts_dir)


def save_api_test_result(config, sentence, true_label, pred_label, evaluation, artifacts_dir):
    artifacts_path = pathlib.Path(artifacts_dir)
    artifacts_path.mkdir(parents=True, exist_ok=True)

    text_fragment = make_meaningful_filename(sentence, 40)
    short_hash = hashlib.sha256(sentence.encode("utf-8")).hexdigest()[:6]
    filename = f"{config.get('task2_short')}_{text_fragment}_{short_hash}.json"
    output_path = artifacts_path / filename

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "model": config.get("model2"),
                "task": config.get("task2"),
                "input": sentence,
                "expected": true_label,
                "output": pred_label,
                "evaluation": evaluation,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def make_meaningful_filename(sentence: str, max_len: int = 40) -> str:
    safe = "".join(c if c.isalnum() else "_" for c in sentence).strip("_")
    return safe[:max_len].rstrip("_")


# Create markdown summary report  
@pytest.mark.order("last")
def test_generate_markdown_summary_sa(config, artifacts_dir, reports_dir):
    md_path = reports_dir / "summary_sa.md"
    generate_markdown_summary_sa(artifacts_dir, md_path)
    assert md_path.exists(), "summary_sa.md should be generated"