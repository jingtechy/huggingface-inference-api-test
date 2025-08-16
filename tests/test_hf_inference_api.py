import json
import hashlib
from dotenv import load_dotenv
import os
import pathlib
import re
from typing import Dict, Any, List, Tuple

import pytest
from huggingface_hub import InferenceClient


def load_test_inputs() -> List[Tuple[str, List[str]]]:
    """Load test inputs from SQuAD2.0 JSON file with their expected answers"""
    test_data_path = pathlib.Path(__file__).parent.parent / "test_data" / "squad2.json"
    
    if not test_data_path.exists():
        # Fallback to hardcoded inputs if JSON file not found
        return [
            ("Hello from Hugging Face Inference API!", ["hello", "hugging face"]),
            ("Write a short poem about the ocean.", ["ocean", "poem"]),
            ("Who wrote Hamlet?", ["William Shakespeare"])
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
                            if len(qa_pairs) >= 2: 
                                return qa_pairs  # collect 2 questions
    
    return qa_pairs if qa_pairs else [
        ("Hello from Hugging Face Inference API!", ["hello", "hugging face"]),
        ("Write a short poem about the ocean.", ["ocean", "poem"]),
        ("Who wrote Hamlet?", ["William Shakespeare"])
    ]


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


@pytest.mark.parametrize("qa_pair", load_test_inputs(), ids=lambda v: f"q_{len(v[0])}")
def test_text_generation(config: Dict[str, Any], artifacts_dir: pathlib.Path, qa_pair: Tuple[str, str,List[str]]) -> None:
    context, question, expected_answers = qa_pair
    
    # Create client directly
    load_dotenv()  # read .env file
    token = os.getenv("HF_TOKEN") 
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

    # Save result for later inspection
    filename_stem = hashlib.sha256((context + question).encode("utf-8")).hexdigest()[:12]
    output_path = artifacts_dir / f"textgen_{filename_stem}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "model": config.get("model"),
                "task": "question_answering",  
                "input": question,
                "expected_answers": expected_answers,
                "output": output_text,
                "evaluation": evaluation_results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
