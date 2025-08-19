# Test Data for Question Answering Model (SQuAD 2.0 Format)

This folder contains a sample dataset in **SQuAD 2.0 JSON format** for testing question-answering (QA) models. It is suitable for evaluating the performance of NLP models on reading comprehension tasks, including handling **answerable** and **unanswerable** questions.

## Dataset Overview

- **File name:** `squad2.0.json`  
- **Format:** JSON (SQuAD 2.0)  
- **Version:** v2.0  
- **Structure:**  
  - `data`: List of articles  
    - `title`: Title of the article  
    - `paragraphs`: List of paragraphs  
      - `context`: The passage text  
      - `qas`: List of question-answer pairs  
        - `question`: The question text  
        - `id`: Unique ID for the question  
        - `answers`: List of answers (empty if unanswerable)  
        - `is_impossible`: Indicates whether the question is unanswerable  
        - `plausible_answers`: Optional suggested answers for unanswerable questions  

## Example Usage

### 1. Loading the Dataset in Python

```python
import json

# Load the dataset
with open("test_data/squad2.0.json", "r", encoding="utf-8") as f:
    squad_data = json.load(f)

# Explore the first article and paragraph
article = squad_data['data'][0]
paragraph = article['paragraphs'][0]
print("Title:", article['title'])
print("Context:", paragraph['context'])
print("First question:", paragraph['qas'][0]['question'])
print("First answer:", paragraph['qas'][0]['answers'][0]['text'])
