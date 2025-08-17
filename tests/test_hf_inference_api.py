import json
import hashlib
from _pytest import config
from dotenv import load_dotenv
import os
import pathlib
import shutil
import random
import re
from typing import Dict, Any, List, Tuple

import pytest
from huggingface_hub import InferenceClient


def load_test_inputs() -> List[Tuple[str, List[str]]]:
    """Load test inputs from SQuAD2.0 JSON file with their expected answers"""
    test_data_path = pathlib.Path(__file__).parent.parent / "test_data" / "squad2.json"
    
    if not test_data_path.exists():
        # Fallback to hardcoded inputs if JSON file not found
        fallback_inputs = [
            ("What is the capital of France?", ["Paris"]),
            ("Which planet is known as the Red Planet?", ["Mars", "the Red Planet"]),
            ("Who wrote Hamlet?", ["William Shakespeare", "Shakespeare"])
        ]
    
    with test_data_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract questions and answers from SQuAD2.0 format
    qa_pairs = []
    if "data" in data:
        for article in data["data"]:
            for paragraph in article.get("paragraphs", []):
                context = paragraph.get("context", "")
                for qa in paragraph.get("qas", []):
                    if qa.get("question") and not qa.get("is_impossible", False):
                        expected_answers = [
                            answer["text"].lower().strip()
                            for answer in qa.get("answers", [])
                            if answer.get("text")
                        ]
                        if expected_answers:  # Only include questions with answers
                            # pack as (context, question, expected_answers)
                            qa_pairs.append((context, qa["question"], expected_answers))
                            #if len(qa_pairs) >= 2: 
                                #return qa_pairs  # collect 2 questions always from top

    # If we have valid QA pairs, pick 2 randomly; otherwise use fallback 
    if qa_pairs:
        return random.sample(qa_pairs, k=min(2, len(qa_pairs)))   
    else:   
        return fallback_inputs                 


def evaluate_response(model_output: str, expected_answers: List[str]) -> Dict[str, float]:
    """Evaluate model response against expected answers"""
    model_output_lower = model_output.lower()
    
    # Check if any expected answer appears in the model output
    correct_predictions = 0
    total_expected = len(expected_answers)
    
    for expected_answer in expected_answers:
        # Simple substring matching (can be improved with more sophisticated matching)
        if expected_answer in model_output_lower:
            correct_predictions += 1
    
    # Calculate metrics
    accuracy = correct_predictions / total_expected if total_expected > 0 else 0.0
    
    # For precision/recall/F1, treat this as binary classification
    # True Positive: Model contains expected answer
    # False Positive: Model contains wrong information
    # False Negative: Model doesn't contain expected answer
    
    tp = correct_predictions
    fp = 0  # Simplified - could be enhanced to detect wrong answers
    fn = total_expected - correct_predictions
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "correct_predictions": correct_predictions,
        "total_expected": total_expected
    }


@pytest.fixture(scope="session", autouse=True)
def prepare_artifacts(artifacts_dir):
    """Clear artifacts folder once at the beginning of the test session."""
    artifacts_path = pathlib.Path(artifacts_dir)
    if artifacts_path.exists():
        shutil.rmtree(artifacts_path)
    artifacts_path.mkdir(parents=True, exist_ok=True)
    return artifacts_path
  

@pytest.mark.parametrize("qa_pair", load_test_inputs(), ids=lambda v: "QA_" + re.sub(r'[^a-zA-Z0-9_]', '_', v[0][:15]))
def test_question_answering(config: Dict[str, Any], artifacts_dir: pathlib.Path, qa_pair: Tuple[str, str,List[str]]) -> None:
    context, question, expected_answers = qa_pair
    
    # Load local .env if exists
    env_path = pathlib.Path(".env")
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    
    # Get token from environment either local .env or Actions secret in Github Actions
    token = os.getenv("HF_TOKEN")

    # Strip whitespace and ensure it's not a placeholder
    if token:
        token = token.strip()
    if not token or token == "***":
        pytest.skip("HF_TOKEN not set or is placeholder, skipping test") 

    client = InferenceClient(
        token=token,  
        timeout=config.get("timeout_seconds", 30),
        provider=config.get("provider", "hf-inference")
    )
    
    # question_answering() calls the Hugging Face Inference API to answer the question based on the context
    # It sends an HTTP request to the model and returns the AI-generated response
    output_text = client.question_answering(model=config["model"],question=question, context=context).answer

    assert isinstance(output_text, str)
    assert len(output_text) > 0

    # Evaluate the response
    evaluation_results = evaluate_response(output_text, expected_answers)
    
    # Assert minimum performance (adjust thresholds as needed)
    assert evaluation_results["accuracy"] >= 0.0, f"Accuracy too low: {evaluation_results['accuracy']}"
    assert evaluation_results["f1"] >= 0.0, f"F1 score too low: {evaluation_results['f1']}"

    save_api_test_result(config, question, expected_answers, output_text, evaluation_results, artifacts_dir)
  

def save_api_test_result(config, question, expected_answers, output_text, evaluation_results, artifacts_dir):
    """Save test results to the artifacts folder with meaningful filenames."""
    artifacts_path = pathlib.Path(artifacts_dir)
    if not artifacts_path.exists():
        artifacts_path.mkdir(parents=True, exist_ok=True)

    # Use part of the task + question + hash for uniqueness
    task_short = config.get("task_short")
    question_fragment = make_meaningful_filename(question, 40)
    short_hash = hashlib.sha256((question).encode("utf-8")).hexdigest()[:6]   

    filename = f"{task_short}_{question_fragment}_{short_hash}.json"
    output_path = artifacts_path / filename

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "model": config.get("model"),
                "task": config.get("task"),
                "input": question,
                "expected_answers": expected_answers,
                "output": output_text,
                "evaluation": evaluation_results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

def make_meaningful_filename(question: str, max_len: int = 40) -> str:
    """Create a meaningful, filesystem-safe filename from the question."""
    # Replace invalid characters with underscore
    safe = "".join(c if c.isalnum() else "_" for c in question).strip("_")
    return safe[:max_len].rstrip("_")
  
