# Scripts & Tools Guide

This guide explains the different scripts and tools available in the project and when to use each one.

---

## 📁 Project Scripts Overview

```
scripts/
├── evaluate_models.py        # Evaluate QUESTION GENERATION quality
└── test_model_answers.py     # Evaluate MODEL ANSWER performance

examples/notebooks/
├── 01_question_generation.py # Interactive question generation
└── 02_model_evaluation.py    # Interactive model testing
```

---

## 1. Question Generation Quality Evaluation

**Script**: `scripts/evaluate_models.py`

### Purpose
Evaluates how well different LLM models **generate educational questions** from content.

### Use When
- Comparing different models for question generation
- Assessing quality of generated questions
- Choosing the best model for your use case
- Testing grading consistency

### Metrics
- **Answerability**: Can questions be answered from source?
- **Coherence**: Are questions well-formed?
- **Difficulty Distribution**: Balance of easy/medium/hard
- **Grading Consistency**: Reproducibility of grading
- **Cost per Question**: API cost estimates

### Usage
```bash
# Compare multiple models for question generation
python scripts/evaluate_models.py \
    --models gpt-4o-mini,gpt-4o \
    --content examples/medical_content.md \
    --num-questions 10

# Use specific output directory
python scripts/evaluate_models.py \
    --models gpt-4o-mini \
    --content data/uploads/myfile.md \
    --num-questions 20 \
    --output-dir custom_evaluations/
```

### Output
- Location: `data/out/evaluations/evaluation_YYYYMMDD_HHMMSS.json`
- Contains: Quality scores, consistency metrics, model rankings
- Format:
  ```json
  {
    "model_results": {
      "gpt-4o-mini": {
        "quality_score": 0.85,
        "consistency_score": 0.92,
        "avg_generation_time": 2.3,
        "cost_per_question": 0.000075
      }
    },
    "recommendations": {
      "recommended_model": "gpt-4o-mini",
      "reasoning": "Best balance of quality and cost"
    }
  }
  ```

---

## 2. Model Answer Performance Evaluation

**Script**: `scripts/test_model_answers.py`

### Purpose
Tests how well different LLM models **answer existing exam questions**.

### Use When
- Measuring AI-pass rate (what % of questions can AI solve)
- Comparing model performance on specific exams
- Identifying AI-resistant question types
- Benchmarking for educational assessment design

### Metrics
- **Accuracy**: Percentage of correct answers
- **AI Pass Rate**: Same as accuracy
- **Per-Question Breakdown**: Detailed results for each question
- **Type-Specific Performance**: Accuracy by question type

### Usage

#### Test Single Model
```bash
python scripts/test_model_answers.py \
    --exam data/out/exam_ex-123.json \
    --model gpt-4o-mini \
    --provider openai
```

#### Compare Multiple Models
```bash
# Compares predefined models (GPT + Yandex if available)
python scripts/test_model_answers.py \
    --exam data/out/exam_ex-123.json \
    --compare
```

#### Test on All Exams in Directory
```bash
python scripts/test_model_answers.py \
    --exam-dir data/out \
    --model yandexgpt-lite \
    --provider yandex \
    --language ru
```

### Output
- Location: `data/results/`
- Individual tests: `model_test_{model}_{exam_id}_{timestamp}.json`
- Comparisons: `model_comparison_{exam_id}_{timestamp}.json`
- Format:
  ```json
  {
    "model_name": "gpt-4o-mini",
    "provider": "openai",
    "accuracy": 0.85,
    "correct_count": 17,
    "total_questions": 20,
    "per_question_results": [...]
  }
  ```

---

## 3. Interactive Question Generation (Jupyter)

**Script**: `examples/notebooks/01_question_generation.py`

### Purpose
Interactive, Jupyter-friendly functions for generating questions from content.

### Use When
- Experimenting with question generation in notebooks
- Quick prototyping
- Custom question generation workflows
- Teaching/demonstration purposes

### Key Functions

#### Generate Full Exam
```python
from examples.notebooks.question_generation import generate_exam, save_exam

exam = generate_exam(
    "data/uploads/myfile.md",
    total_questions=20,
    single_choice_ratio=0.5,
    multiple_choice_ratio=0.3,
    open_ended_ratio=0.2,
    language="ru"
)

save_exam(exam, "my_exam.json")
```

#### Generate Single Question
```python
from examples.notebooks.question_generation import generate_single_question

question = generate_single_question(
    content="Photosynthesis is...",
    question_type="single_choice",
    difficulty="medium",
    provider="openai"  # or "yandex"
)

print(question["stem"])
print(question["options"])
```

#### From Text Content (No File Required)
```python
content = """
# Topic Name
## Section 1
Content here...
"""

question = generate_single_question(
    content=content,
    question_type="open_ended",
    difficulty="hard",
    language="en"
)
```

### Running Examples
```bash
# Run examples directly
python examples/notebooks/01_question_generation.py

# Or in Jupyter
%run examples/notebooks/01_question_generation.py
```

---

## 4. Interactive Model Evaluation (Jupyter)

**Script**: `examples/notebooks/02_model_evaluation.py`

### Purpose
Interactive, Jupyter-friendly functions for testing models on exams.

### Use When
- Quick model testing in notebooks
- Exploratory analysis
- Custom evaluation workflows
- Research experiments

### Key Functions

#### Test Single Model
```python
from examples.notebooks.model_evaluation import test_model, analyze_result

result = test_model(
    "data/out/exam_ex-123.json",
    model_name="gpt-4o-mini",
    provider="openai",
    language="en"
)

analyze_result(result)
# Outputs: accuracy, type breakdown, failed questions
```

#### Compare Multiple Models
```python
from examples.notebooks.model_evaluation import compare_models, print_comparison

comparison = compare_models(
    "data/out/exam_ex-123.json",
    models=[
        {"model_name": "gpt-4o-mini", "provider": "openai"},
        {"model_name": "yandexgpt-lite", "provider": "yandex"}
    ],
    language="ru"
)

print_comparison(comparison)
# Outputs: best model, accuracy table, hard questions
```

#### Load Exam
```python
from examples.notebooks.model_evaluation import load_exam

exam = load_exam("data/out/exam_ex-123.json")
print(f"Questions: {len(exam.questions)}")
```

### Running Examples
```bash
# Run examples directly (uses first exam in data/out/)
python examples/notebooks/02_model_evaluation.py

# Or in Jupyter
%run examples/notebooks/02_model_evaluation.py
```

---

## 🔄 Common Workflows

### Workflow 1: Generate → Evaluate Quality → Test Models

```bash
# 1. Generate exam from content
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"markdown_content":"...","config":{...}}'

# 2. Evaluate generation quality (optional)
python scripts/evaluate_models.py \
  --models gpt-4o-mini \
  --content myfile.md

# 3. Test models on generated exam
python scripts/test_model_answers.py \
  --exam data/out/exam_ex-123.json \
  --compare
```

### Workflow 2: Jupyter Research Flow

```python
# Generate exam
from examples.notebooks.question_generation import generate_exam, save_exam

exam = generate_exam("content.md", total_questions=20)
exam_file = save_exam(exam)

# Test models
from examples.notebooks.model_evaluation import compare_models

comparison = compare_models(
    exam_file,
    models=[
        {"model_name": "gpt-4o-mini", "provider": "openai"},
        {"model_name": "yandexgpt-lite", "provider": "yandex"}
    ]
)

print(f"Best: {comparison['best_model']}")
print(f"Accuracy: {comparison['best_accuracy']:.2%}")
```

### Workflow 3: Batch Evaluation

```python
from pathlib import Path
from examples.notebooks.model_evaluation import test_model

# Test all exams on single model
exam_files = Path("data/out").glob("exam_*.json")
results = []

for exam_file in exam_files:
    result = test_model(str(exam_file), "gpt-4o-mini", "openai")
    results.append(result)
    print(f"{exam_file.name}: {result.accuracy:.2%}")

avg_accuracy = sum(r.accuracy for r in results) / len(results)
print(f"\nAverage accuracy: {avg_accuracy:.2%}")
```

---

## 🎯 Quick Decision Guide

**I want to...**

| Task | Use This |
|------|----------|
| Compare models for question generation quality | `scripts/evaluate_models.py` |
| See how well models answer existing questions | `scripts/test_model_answers.py` |
| Generate questions interactively in Jupyter | `examples/notebooks/01_question_generation.py` |
| Test models interactively in Jupyter | `examples/notebooks/02_model_evaluation.py` |
| Generate questions from text (no file) | `01_question_generation.py::generate_single_question()` |
| Generate questions from .md file | `01_question_generation.py::generate_exam()` |
| Batch test multiple models | `scripts/test_model_answers.py --compare` |
| Custom evaluation pipeline | Use notebook functions as library |

---

## 💡 Tips

1. **For Production**: Use CLI scripts (`scripts/*.py`) - they're optimized and stable
2. **For Research**: Use notebook functions (`examples/notebooks/*.py`) - they're flexible
3. **Question Generation**: Always evaluate quality before using questions in real exams
4. **Model Testing**: Test on diverse question types to get representative results
5. **Cost Management**: Use `gpt-4o-mini` and `yandexgpt-lite` for development

---

## 📚 See Also

- **Complete Evaluation Guide**: `docs/EVALUATION.md`
- **API Reference**: `docs/SOLUTION_OVERVIEW.md`
- **Quick Start**: `README.md`
