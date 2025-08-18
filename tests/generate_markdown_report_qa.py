import datetime as _dt
import json
import pathlib
from typing import Iterable

import pytest

from tests.conftest import config


def _sanitize_markdown_cell(text: str) -> str:
    # Replace pipe to avoid breaking Markdown table cells
    return text.replace("|", "&#124;")

def generate_markdown_summary(artifacts_dir: pathlib.Path, report_path: pathlib.Path) -> None:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    items: list[dict] = []
    total_em = 0.0
    total_f1 = 0.0
    total_tests = 0
    
    for path in artifacts_dir.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extract evaluation metrics if available
            evaluation = data.get("evaluation", {})
            em = evaluation.get("exact_match", 0.0)
            f1 = evaluation.get("f1", 0.0)
            
            # Accumulate totals for averaging
            total_em += em
            total_f1 += f1
            total_tests += 1

            def _truncate(text: str, max_len: int) -> str:
             return text if len(text) <= max_len else text[:max_len] + "…"
            
            # Truncated long text (input, expected_answers, output) to a reasonable length
            # Converted lists to comma-separated strings for input and expected_answers, so the table can render them as text
            items.append({
                #"file": path.name,
                "model": data.get("model"),
                "task": data.get("task"),
                "unanswerable": data.get("is_impossible"),
                "input": _truncate(str(data.get("input", "")).replace("\n", " "), 200),
                "expected_answers": _truncate(", ".join(data.get("expected_answers", [])) if isinstance(data.get("expected_answers", []), list) else str(data.get("expected_answers", "")), 80),
                "output": _truncate(str(data.get("output", "")).replace("\n", " "), 200),
                "em": f"{em:.3f}",
                "f1": f"{f1:.3f}"
            })
        except Exception:
            continue

    lines: list[str] = []
    lines.append(f"# Hugging Face Inference API Test Summary — {_dt.datetime.now().isoformat(timespec='seconds')}\n")
    
    if not items:
        lines.append("No artifacts were found.\n")
    else:
        # Calculate averages
        avg_em = total_em / total_tests if total_tests > 0 else 0.0
        avg_f1 = total_f1 / total_tests if total_tests > 0 else 0.0
        
        # Summary statistics
        lines.append("## Summary Statistics\n")
        lines.append(f"- **Total Tests**: {total_tests}\n")
        lines.append(f"- **Average Exact Match**: {avg_em:.3f}\n")
        lines.append(f"- **Average F1 Score**: {avg_f1:.3f}\n\n")

        # After collecting all items
        items.sort(key=lambda x: (x["task"], x["model"]))
        
        # No wrap at all so show one line all together
        def _no_wrap(text: str) -> str:
            return text.replace(" ", "&nbsp;") # Replace spaces with non-breaking spaces to keep words together
        
        # Wrap after every 5 words
        def _soft_wrap(text: str, words_per_line: int = 5) -> str:
          words = text.split()
          chunks = [
             "&nbsp;".join(words[i:i+words_per_line]) # group words with non-breaking spaces
             for i in range(0, len(words), words_per_line)
          ]
          return "\u200b".join(chunks) # allow wrapping only between chunks
          
        
        # Detailed results table
        lines.append("## Detailed Results\n")
        lines.append("| Model | Task | Unanswerable | Input | Expected Answers | Output | Exact Match | F1 Score |\n")
        lines.append("|---|---|---|---|---|---|---|---|\n")

        for it in items:
            model = _sanitize_markdown_cell(str(it['model']))
            task = _sanitize_markdown_cell(str(it['task']))
            unanswerable = it['unanswerable']

            input_cell = _soft_wrap(_sanitize_markdown_cell(it['input']))
            expected_answers = _soft_wrap(_sanitize_markdown_cell(it['expected_answers']))
            output_cell = _soft_wrap(_sanitize_markdown_cell(it['output']))

            em = it['em']
            f1 = it['f1']
            lines.append(f"| {model} | {task} | {unanswerable} | {input_cell} | {expected_answers} | {output_cell} | {em} | {f1} |\n")

    with report_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)

  