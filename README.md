# huggingface-inference-api-test

Pytest automation for Hugging Face Inference API.

# Features

## Automatic API Calls
- Calls Hugging Face Inference API for supported tasks.  
- **Default task:** `question_answering` for SQuAD-style test data.  
- **Configurable model:** via `config.yml` or environment variable `HF_TOKEN`.  
- **Example free models for QA:** `deepset/roberta-base-squad2`.  

## Test Data Support
- Can load **SQuAD 2.0 JSON files** or fallback hardcoded examples.  
- Supports **both answerable and unanswerable questions** (for QA tasks).  
- **Parameterized tests** allow running multiple QA pairs or prompts.  

## Model Evaluation
- Automatically evaluates model outputs against expected answers.  
- Supports common NLP evaluation metrics:
  - **Accuracy** — fraction of correctly predicted answers  
  - **Precision** — proportion of relevant answers among predicted answers  
  - **Recall** — proportion of relevant answers captured  
  - **F1 Score** — harmonic mean of precision and recall  

## Custom Reports
- Saves model outputs in `artifacts/` for reproducibility.  
- Generates **HTML report** (`reports/report.html`) and **JUnit XML** (`reports/junit.xml`).  
- Generates **custom markdown summary reports** (`reports/summary.md`), aggregating metrics across all test cases for easy inspection.  

## Configuration & Extensibility
- Configurable via `config.yml` and environment variables.  
- Supports **custom model parameters** like temperature, max tokens, etc.  
- Easy to extend for new models, tasks, or evaluation metrics.

## Requirements
- Python 3.9+
- A Hugging Face token with Inference API access (set `HF_TOKEN`)

## Quickstart
1. Set your token:
   - macOS/Linux:
     ```bash
     export HF_TOKEN=hf_xxx_your_token_here
     ```
   - Windows PowerShell
     ```bash
     $env:HF_TOKEN="hf_xxx_your_token_here"
     ```
2. Create virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run tests:
   ```bash
   pytest -q
   ```

4. View results:
   - Open `reports/report.html` for the HTML report
   - Check `reports/summary.md` for the Markdown summary
   - API outputs are saved in `artifacts/`