# Hugging Face Inference API Test

This project enables testing AI models using the Hugging Face Inference API and evaluating their performance with standard metrics. Users can run model predictions, calculate metrics such as accuracy, precision, recall, and F1-score, and generate detailed reports.

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

## Continuous Integration (CI)

This project uses **GitHub Actions** for Continuous Integration. The workflow automatically runs tests whenever code is pushed or a pull request is created.

### Workflow Status

![CI Status](https://github.com/jingtechy/huggingface-inference-api-test/actions/workflows/ci.yml/badge.svg)

### Details

- **Workflow file:** `.github/workflows/ci.yml`
- **Runs on:** Push to main and feature branches and on Pull Requests
- **Tasks included:** 
  - **Checkout repository** – Retrieves the latest code from the repository
  - **Cache pip dependencies** – Speeds up workflow runs by caching Python packages
  - **Set up Python** – Installs Python 3.13 on the runner
  - **Install dependencies** – Installs all required packages from `requirements.txt`
  - **Run tests**:
   - **Fast feedback** on push events: Runs pytest with a maximum of 1 failure (`--maxfail=1`) for quick feedback
   - **Full test run** on pull requests: Runs all tests without early exit
  - **Generate test reports**:
   - **HTML report** (`reports/report.html`)
   - **JUnit XML report** (`reports/junit.xml`)
   - **Summary Markdown** (`reports/summary.md`)
  - **Upload artifacts** – Stores reports as GitHub Actions artifacts for later download and inspection 

## Requirements
- Python 3.11
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
2. Install Python 3.11 using Homebrew  
     ```bash
     brew install python@3.11
     ```   
3. Create virtual environment and install dependencies:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run tests:
   ```bash
   pytest -q
   ```
5. View results:
   - Open `reports/report.html` for the HTML report
   - Check `reports/summary.md` for the Markdown summary
   - API outputs are saved in `artifacts/`