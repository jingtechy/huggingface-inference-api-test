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

from tests.conftest import artifacts_dir, reports_dir
from tests.generate_markdown_report_qa import generate_markdown_summary


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
                    question = qa.get("question", "")
                    is_impossible = qa.get("is_impossible")
                    #if qa.get("question") and not qa.get("is_impossible", False):   # Only include answerable questions
                    expected_answers = [
                        answer["text"].lower().strip()
                        for answer in qa.get("answers", [])
                        if answer.get("text")
                    ] 
                    # Include both answerable and unanswerable questions
                    qa_pairs.append((context, question, expected_answers, is_impossible))
                    #if len(qa_pairs) >=2:
                        #return qa_pairs  # collect 2 questions always from top                                

    # If we have valid QA pairs, pick 2 randomly; otherwise use fallback 
    if qa_pairs:
        return random.sample(qa_pairs, k=min(2, len(qa_pairs)))   
    else:   
        return fallback_inputs                 

def normalize_answer(s: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)
    def white_space_fix(text):
        return ' '.join(text.split())
    def remove_punc(text):
        return re.sub(r'[^\w\s]', '', text)
    def lower(text):
        return text.lower()
    return white_space_fix(remove_articles(remove_punc(lower(s))))

def f1_score(prediction: str, ground_truth: str) -> float:
    pred_tokens = normalize_answer(prediction).split()
    gt_tokens = normalize_answer(ground_truth).split()
    common = set(pred_tokens) & set(gt_tokens)
    num_same = sum(min(pred_tokens.count(token), gt_tokens.count(token)) for token in common)
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gt_tokens)
    return 2 * precision * recall / (precision + recall)

def exact_match_score(prediction: str, ground_truth: str) -> float:
    return float(normalize_answer(prediction) == normalize_answer(ground_truth))

def evaluate_response(prediction: str, expected_answers: List[str], is_impossible: bool) -> Tuple[str, float]:
    """
    Returns (EM, F1) for a single QA pair.
    - For unanswerable questions (is_impossible=True):
        - prediction="" → EM=1, F1=1
        - prediction!= "" → EM=0, F1=0
    - For answerable questions:
        - Take max EM/F1 over all expected_answers
    """
    if is_impossible: # Unanswerable
        if prediction.strip() == "":
            return {"em": 1.0, "f1": 1.0}
        else:
            return {"em": 0.0, "f1": 0.0}
    else:  # Answerable
        if prediction.strip() == "":  # Treat as unanswerable
            return {"em": 0.0, "f1": 0.0}
        em = max(exact_match_score(prediction, ans) for ans in expected_answers)
        f1 = max(f1_score(prediction, ans) for ans in expected_answers)

    return {
        "exact_match": em,
        "f1": f1
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
def test_question_answering(config: Dict[str, Any], artifacts_dir: pathlib.Path, qa_pair: Tuple[str, str,List[str], bool]) -> None:
    context, question, expected_answers, is_impossible = qa_pair
    
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
    result = client.question_answering(model=config["model"], question=question, context=context)
    raw_output = result.answer if isinstance(result, dict) else ""
    output = raw_output if isinstance(raw_output, str) else str(raw_output) # Make sure output always return a (or empty) string
    
    assert isinstance(output, str)
    # Evaluate the response
    evaluation_results = evaluate_response(output, expected_answers, is_impossible)

    save_api_test_result(config, question, expected_answers, output, evaluation_results, is_impossible, artifacts_dir)

def save_api_test_result(config, question, expected_answers, output, evaluation_results, is_impossible, artifacts_dir):
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
                "is_impossible": is_impossible,
                "input": question,
                "expected_answers": expected_answers,
                "output": output,
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

# Create markdown summary report  
@pytest.mark.order("last")
def test_generate_markdown_summary(config, artifacts_dir, reports_dir):
    md_path = reports_dir / "summary.md"
    generate_markdown_summary(artifacts_dir, md_path)
    assert md_path.exists(), "summary.md should be generated"