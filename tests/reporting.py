import datetime as _dt
import json
import pathlib
from typing import Iterable


def _sanitize_markdown_cell(text: str) -> str:
    # Replace pipe to avoid breaking Markdown table cells
    return text.replace("|", "&#124;")


def generate_markdown_summary(artifacts_dir: pathlib.Path, report_path: pathlib.Path) -> None:
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
            
            items.append({
                "file": path.name,
                "model": data.get("model"),
                "task": data.get("task"),
                "input": data.get("input"),
                "expected_answers": data.get("expected_answers", []),
                "output_preview": str(data.get("output", ""))[:200].replace("\n", " "),
                "accuracy": f"{accuracy:.3f}",
                "precision": f"{precision:.3f}",
                "recall": f"{recall:.3f}",
                "f1": f"{f1:.3f}"
            })
        except Exception:
            continue

    lines: list[str] = []
    lines.append(f"# Inference Summary — {_dt.datetime.now().isoformat(timespec='seconds')}\n")
    
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
        
        # Detailed results table
        lines.append("## Detailed Results\n")
        lines.append("| File | Model | Task | Input | Expected Answers | Output (preview) | Accuracy | Precision | Recall | F1 |\n")
        lines.append("|---|---|---|---|---|---|---|---|---|---|\n")
        for it in items:
            file = _sanitize_markdown_cell(it['file'])
            model = _sanitize_markdown_cell(str(it['model']))
            task = _sanitize_markdown_cell(str(it['task']))
            input_cell = _sanitize_markdown_cell(str(it['input']))
            expected_answers = _sanitize_markdown_cell(str(it['expected_answers']))
            output_cell = _sanitize_markdown_cell(it['output_preview'])
            accuracy = it['accuracy']
            precision = it['precision']
            recall = it['recall']
            f1 = it['f1']
            lines.append(f"| {file} | {model} | {task} | {input_cell} | {expected_answers} | {output_cell} | {accuracy} | {precision} | {recall} | {f1} |\n")

    with report_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)
