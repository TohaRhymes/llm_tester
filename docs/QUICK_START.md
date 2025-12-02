# Quick Start Guide

Get started with LLM Test Generator in 5 minutes.

---

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/TohaRhymes/llm_tester.git
cd llm_tester

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys
```

---

## 🔑 Environment Setup

### Required (OpenAI)
```bash
OPENAI_API_KEY=sk-proj-your-key-here
```

### Optional (Yandex Cloud)
```bash
YANDEX_CLOUD_API_KEY=AQVN...
YANDEX_CLOUD_API_KEY_IDENTIFIER=ajei...
YANDEX_FOLDER_ID=b1g...
```

Get Yandex credentials: https://console.cloud.yandex.ru/

---

## 📝 Example 1: Generate Questions from Markdown File

### Step 1: Create Content File

Create `my_content.md`:
```markdown
# Photosynthesis

## Overview
Photosynthesis is the process by which plants use sunlight to convert carbon dioxide and water into glucose and oxygen. This occurs in chloroplasts.

## Key Components
- Chlorophyll: green pigment that absorbs light
- Light reactions: occur in thylakoids
- Calvin cycle: occurs in stroma
```

### Step 2: Generate Exam

#### Using API
```bash
# Start server
uvicorn app.main:app --reload

# Generate exam
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "# Photosynthesis\n\n## Overview\nPhotosynthesis is...",
    "config": {
      "total_questions": 5,
      "single_choice_ratio": 0.6,
      "multiple_choice_ratio": 0.2,
      "open_ended_ratio": 0.2
    }
  }'
```

#### Using Python
```python
from examples.notebooks.question_generation import generate_exam, save_exam

# Generate exam from file
exam = generate_exam(
    "my_content.md",
    total_questions=10,
    language="en"
)

# Save exam
exam_file = save_exam(exam)
print(f"Exam saved to: {exam_file}")

# View questions
for q in exam.questions:
    print(f"\n{q.id}: {q.stem}")
    if q.type != "open_ended":
        for i, opt in enumerate(q.options):
            print(f"  {i}. {opt}")
```

---

## 📝 Example 2: Generate Questions from Text (No File)

```python
from examples.notebooks.question_generation import generate_single_question

# Direct text input
content = """
Machine learning is a subset of artificial intelligence that focuses on
algorithms that learn from data. It includes supervised learning,
unsupervised learning, and reinforcement learning approaches.
"""

# Generate single choice question
question = generate_single_question(
    content=content,
    question_type="single_choice",
    difficulty="medium",
    provider="openai"
)

print("Question:", question["stem"])
print("Options:")
for i, opt in enumerate(question["options"]):
    print(f"  {i}. {opt}")
print("Correct:", question["correct"])
```

---

## 🧪 Example 3: Test How Well Models Answer Questions

### Test Single Model
```bash
python scripts/test_model_answers.py \
  --exam data/out/exam_ex-123.json \
  --model gpt-4o-mini \
  --provider openai
```

### Compare Multiple Models
```bash
python scripts/test_model_answers.py \
  --exam data/out/exam_ex-123.json \
  --compare
```

### Using Python
```python
from examples.notebooks.model_evaluation import test_model, compare_models

# Test one model
result = test_model(
    "data/out/exam_ex-123.json",
    "gpt-4o-mini",
    "openai"
)
print(f"Accuracy: {result.accuracy:.2%}")

# Compare models
comparison = compare_models(
    "data/out/exam_ex-123.json",
    models=[
        {"model_name": "gpt-4o-mini", "provider": "openai"},
        {"model_name": "yandexgpt-lite", "provider": "yandex"}
    ]
)
print(f"Best: {comparison['best_model']} ({comparison['best_accuracy']:.2%})")
```

---

## 📊 Example 4: Complete Workflow

```python
# 1. Generate exam from content
from examples.notebooks.question_generation import generate_exam, save_exam

exam = generate_exam(
    "my_content.md",
    total_questions=20,
    single_choice_ratio=0.5,
    multiple_choice_ratio=0.3,
    open_ended_ratio=0.2
)
exam_file = save_exam(exam)

# 2. Test models on exam
from examples.notebooks.model_evaluation import compare_models, print_comparison

comparison = compare_models(
    exam_file,
    models=[
        {"model_name": "gpt-4o-mini", "provider": "openai"},
        {"model_name": "gpt-4o", "provider": "openai"}
    ]
)

print_comparison(comparison)

# 3. Analyze results
print(f"\nBest Model: {comparison['best_model']}")
print(f"Accuracy: {comparison['best_accuracy']:.2%}")

# Find hardest questions (where all models failed)
hard_questions = [
    q_id for q_id, data in comparison['per_question_breakdown'].items()
    if not data['models_correct']
]
print(f"\nQuestions where ALL models failed: {len(hard_questions)}")
```

---

## 🔥 Common Use Cases

### Use Case 1: Generate Russian Questions
```python
from examples.notebooks.question_generation import generate_exam, save_exam

exam = generate_exam(
    "russian_content.md",
    total_questions=15,
    language="ru"  # Russian language
)
save_exam(exam, "russian_exam.json")
```

### Use Case 2: Generate Only Open-Ended Questions
```python
from examples.notebooks.question_generation import generate_exam

exam = generate_exam(
    "content.md",
    total_questions=10,
    single_choice_ratio=0.0,
    multiple_choice_ratio=0.0,
    open_ended_ratio=1.0  # 100% open-ended
)
```

### Use Case 3: Batch Test All Exams
```python
from pathlib import Path
from examples.notebooks.model_evaluation import test_model

results = []
for exam_file in Path("data/out").glob("exam_*.json"):
    result = test_model(str(exam_file), "gpt-4o-mini", "openai")
    results.append((exam_file.name, result.accuracy))

# Print summary
for name, accuracy in sorted(results, key=lambda x: x[1]):
    print(f"{name}: {accuracy:.2%}")
```

### Use Case 4: Custom Difficulty Distribution
```python
from examples.notebooks.question_generation import generate_single_question

# Generate 5 easy, 3 medium, 2 hard questions
questions = []

for _ in range(5):
    q = generate_single_question(content, difficulty="easy")
    questions.append(q)

for _ in range(3):
    q = generate_single_question(content, difficulty="medium")
    questions.append(q)

for _ in range(2):
    q = generate_single_question(content, difficulty="hard")
    questions.append(q)
```

---

## 🐛 Troubleshooting

### Error: OPENAI_API_KEY not set
```bash
# Make sure .env file exists and contains your key
echo "OPENAI_API_KEY=sk-proj-your-key" >> .env
```

### Error: YandexGPT 401 Unauthorized
```bash
# Check your Yandex credentials
# Get FOLDER_ID from: https://console.cloud.yandex.ru/
export YANDEX_FOLDER_ID=b1g...
```

### No exams found in data/out/
```bash
# Generate an exam first
python -c "
from examples.notebooks.question_generation import generate_exam, save_exam
exam = generate_exam('examples/medical_content.md', total_questions=5)
save_exam(exam)
"
```

---

## 📚 Next Steps

- **Learn about different scripts**: Read `docs/SCRIPTS_GUIDE.md`
- **Understand evaluation**: Read `docs/EVALUATION.md`
- **Explore API**: Read `docs/SOLUTION_OVERVIEW.md`
- **Run tests**: `pytest tests/ -v`
- **Try web UI**: Open http://localhost:8000 after starting server

---

## 💡 Tips

1. **Start Small**: Generate 5-10 questions first to test the workflow
2. **Use Mini Models**: `gpt-4o-mini` and `yandexgpt-lite` are cheaper for development
3. **Check Quality**: Use `scripts/evaluate_models.py` to compare generation quality
4. **Save Results**: All outputs are saved to `data/out/` and `data/results/`
5. **Jupyter Friendly**: All example scripts work in Jupyter notebooks

---

## 🆘 Need Help?

- **Issues**: https://github.com/TohaRhymes/llm_tester/issues
- **Documentation**: `docs/` folder
- **Examples**: `examples/notebooks/` folder
