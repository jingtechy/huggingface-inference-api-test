import datetime as _dt
import json
import pathlib
from typing import Iterable

def _sanitize_markdown_cell(text: str) -> str:
    # Replace pipe to avoid breaking Markdown table cells
    return text.replace("|", "&#124;")

def generate_markdown_summary_sa(artifacts_dir: pathlib.Path, report_path: pathlib.Path) -> None:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    items: list[dict] = []
    total_accuracy = 0.0
    total_precision = 0.0
    total_recall = 0.0
    total_f1 = 0.0
    total_tests = 0
    
    for path in artifacts_dir.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # filter only those with task == "sentiment_analysis"
            if data.get("task") != "sentiment_analysis":
                continue    
            
            # Extract evaluation metrics if available
            evaluation = data.get("evaluation", {})
            accuracy = evaluation.get("accuracy", 0.0)
            precision = evaluation.get("precision", 0.0)
            recall = evaluation.get("recall", 0.0)
            f1 = evaluation.get("f1", 0.0)
            
            # Accumulate totals for averaging
            total_accuracy += accuracy
            total_precision += precision
            total_recall += recall
            total_f1 += f1
            total_tests += 1

            def _truncate(text: str, max_len: int) -> str:
                return text if len(text) <= max_len else text[:max_len] + "…"
            
            # Truncate long text fields
            items.append({
                "model": data.get("model"),
                "task": data.get("task"),
                "input": _truncate(str(data.get("input", "")).replace("\n", " "), 100),
                "expected": data.get("expected"),
                "output": data.get("output"),
                "accuracy": f"{accuracy:.3f}",
                "precision": f"{precision:.3f}",
                "recall": f"{recall:.3f}",
                "f1": f"{f1:.3f}"
            })
        except Exception:
            continue

    lines: list[str] = []
    lines.append(f"# Sentiment Analysis Test Summary — {_dt.datetime.now().isoformat(timespec='seconds')}\n")
    
    if not items:
        lines.append("No artifacts were found.\n")
    else:
        # Calculate averages
        avg_accuracy = total_accuracy / total_tests if total_tests > 0 else 0.0
        avg_precision = total_precision / total_tests if total_tests > 0 else 0.0
        avg_recall = total_recall / total_tests if total_tests > 0 else 0.0
        avg_f1 = total_f1 / total_tests if total_tests > 0 else 0.0
        
        # Summary statistics
        lines.append("## Summary Statistics\n")
        lines.append(f"- **Total Tests**: {total_tests}\n")
        lines.append(f"- **Average Accuracy**: {avg_accuracy:.3f}\n")
        lines.append(f"- **Average Precision**: {avg_precision:.3f}\n")
        lines.append(f"- **Average Recall**: {avg_recall:.3f}\n")
        lines.append(f"- **Average F1 Score**: {avg_f1:.3f}\n\n")

        # Sort items
        items.sort(key=lambda x: (x["task"], x["model"]))

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
        lines.append("| Model | Task | Input | Expected | Output | Accuracy | Precision | Recall | F1 Score |\n")
        lines.append("|---|---|---|---|---|---|---|---|---|\n")

        for it in items:
            model = str(it['model'])
            task = str(it['task'])
            input_cell = _soft_wrap(_sanitize_markdown_cell(it['input']))
            expected_cell = str(it['expected'])
            output_cell = str(it['output'])
            lines.append(f"| {model} | {task} | {input_cell} | {expected_cell} | {output_cell} | {it['accuracy']} | {it['precision']} | {it['recall']} | {it['f1']} |\n")

    with report_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)
