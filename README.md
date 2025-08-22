# Hugging Face Inference API Test

This project enables automated testing of AI models using the **Hugging Face Inference API**.  
It supports running model predictions on benchmark datasets, evaluating performance with standard metrics (e.g., accuracy, precision, recall, F1-score, exact match), and generating detailed reports for analysis and comparison.

# 🚀 Features

## 🔗 Automatic API Calls
- Integrates directly with the **Hugging Face Inference API**.  
- Supports multiple tasks:
  - **Question Answering** → SQuAD-style data
  - **Sentiment Analysis** → financial domain data  
- Configurable model selection via `config.yml` or `HF_TOKEN` environment variable.  

## 📂 Test Data Support
- **Question Answering**  
  - Model: [`deepset/roberta-base-squad2`](https://huggingface.co/deepset/roberta-base-squad2)  
  - Dataset: **SQuAD 2.0** ([link](https://rajpurkar.github.io/SQuAD-explorer/))  
  - Includes both **answerable** and **unanswerable** questions.  
- **Sentiment Analysis**  
  - Model: [`distilbert/distilbert-base-uncased-finetuned-sst-2-english`](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)  
  - Dataset: **Financial Sentiment Analysis** from Kaggle ([link](https://www.kaggle.com/datasets/sbhatti/financial-sentiment-analysis))  
  - Labeled examples for **positive**, **negative**, and **neutral** financial sentiment.  

## 📊 Model Evaluation
Evaluation is performed with task-appropriate metrics:

- **Question Answering**
  - **Exact Match** → measures the percentage of predictions that match the ground truth exactly  
  - **F1 Score** → measures word overlap between prediction and ground truth (more forgiving than EM)  

- **Sentiment Analysis**
  - **Accuracy** → fraction of correctly classified samples  
  - **Precision** → proportion of positive identifications that were correct  
  - **Recall** → proportion of actual positives correctly identified  
  - **F1 Score** → harmonic mean of precision and recall  

## 📝 Custom Reports
- Saves all model outputs in `artifacts/` for reproducibility.  
- Generates detailed reports:
  - **HTML Report** → `reports/report.html`
  - **JUnit XML Report** → `reports/junit.xml`
  - **Markdown Summaries** → `reports/summary_qa.md`, `reports/summary_sa.md`  
- Reports include **per-sample evaluations** (perdictions with metrics) and **summary statistics** across the dataset.  

## ⚙️ Configuration & Extensibility
- Easily configurable via `config.yml` and environment variables.  
- Supports optional model parameters (e.g., `temperature`, `max_tokens`).  
- Designed for extensibility:
  - Add new tasks  
  - Plug in different models or datasets  
  - Define custom evaluation metrics  

## Continuous Integration (CI)

This project includes a **GitHub Actions CI workflow** to automatically test Hugging Face inference API integrations.  
The workflow ensures code quality and reliability by running tests on every **push** and **pull request**.

### Workflow Status

![CI Status](https://github.com/jingtechy/huggingface-inference-api-test/actions/workflows/ci.yml/badge.svg)

### 🔄 Workflow Triggers
- **Push events** on:
  - `main`
  - `feature/*`
- **Pull requests** targeting `main`

### 🛠️ Job: `test`
Runs on **Ubuntu (latest)** with the following steps:

1. **Checkout Repository**
   - Uses [`actions/checkout`](https://github.com/actions/checkout) to clone the repository into the runner.

2. **Cache Python Dependencies**
   - Uses [`actions/cache`](https://github.com/actions/cache) to speed up installs by caching `~/.cache/pip`.

3. **Set up Python 3.11**
   - Uses [`actions/setup-python`](https://github.com/actions/setup-python) to install Python 3.11.

4. **Install Dependencies**
   - Upgrades `pip` and installs requirements from `requirements.txt`.

5. **Run Tests with Pytest**
   - **Push events** → Runs tests in *fast feedback mode* (stops after 1 failure).
   - **Pull requests** → Runs the *full test suite*.
   - Generates:
     - **JUnit XML report**
     - **HTML test report**

6. **Upload Artifacts**
   - Test results are uploaded as GitHub Action artifacts:
     - ✅ `pytest-report` → HTML test report
     - 📄 `junit-xml` → JUnit XML results (useful for CI integrations)
     - 📝 `summary-markdown` → Markdown summaries (e.g., `summary_qa.md`, `summary_sa.md`)

### 🔐 Environment Variables
- **`HF_TOKEN`**: Required Hugging Face access token (stored securely in GitHub Secrets).

### 📊 Test Reports
After the workflow completes, you can download artifacts directly from the **GitHub Actions run summary**:
- Open the workflow run → scroll down to **Artifacts** → download reports.

## Requirements
- Python 3.11
- A Hugging Face token with Inference API access (set `HF_TOKEN`)

## Quickstart
1. Set your token:
   - macOS/Linux:
     ```bash
     export HF_TOKEN=hf_xxx_your_token_here
     ```
   - Windows PowerShell:
     ```bash
     $env:HF_TOKEN="hf_xxx_your_token_here"
     ```
2. Install Python 3.11 using Homebrew:  
     ```bash
     brew install python@3.11
     ```   
3. Create virtual environment and install dependencies:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Launch FastAPI app:
   ```bash
   uvicorn apiapp:app --reload --host 0.0.0.0 --port 8000 
   ``` 
5. View built-in UI Interface of FastAPI:
   ```bash
   http://localhost:8000/docs 
   ```  
   Or
    ```bash
   http://localhost:8000/redoc
   ``` 
6. Run tests:
   ```bash
   pytest 
   ```
7. View results:
   - Open `reports/report.html` for the HTML report
   - Check `reports/summary_qa.md`, `reports/summary_sa.md` for the Markdown summary reports
   - API outputs are saved in `artifacts/`

8. Install Streamlit:
   ```bash
   source .venv/bin/activate  
   pip install streamlit 
   ```
9. Launch Streamlit dashboard app:
   ```bash
   streamlit run streamlitapp.py --server.port 8501 
   ```  
10. View Streamlit dashboard:
    ```bash
    http://localhost:8501/
    ```    

## 📊 Test Reports

- **HTML Report:**

![HTML Report](images/html_report.png)

- **Markdown Summary Report:** 

![Question Answering](images/summary_qa.png)

![Sentiment Analysis](images/summary_sa.png)
       