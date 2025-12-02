# Documentation Index

Complete guide to LLM Test Generator documentation.

---

## 📖 Documentation Structure

### For New Users

1. **[Quick Start Guide](QUICK_START.md)** ⭐ **START HERE**
   - 5-minute setup and examples
   - Generate questions from files and text
   - Test models on exams
   - Complete workflow examples

### For Understanding the Tools

2. **[Scripts Guide](SCRIPTS_GUIDE.md)** 📚
   - Detailed explanation of all scripts
   - When to use each tool
   - CLI vs Jupyter examples
   - Common workflows

### For Evaluation & Research

3. **[Evaluation Guide](EVALUATION.md)** 📊
   - Two evaluation systems explained
   - Question generation quality metrics
   - Model answer performance metrics
   - Best practices and workflows

### For Developers

4. **[Solution Overview](SOLUTION_OVERVIEW.md)** 🏗️
   - Architecture and code structure
   - API reference
   - Data contracts
   - Configuration options

---

## 🗂️ Quick Reference

### I want to...

| Goal | Documentation | Tool/Script |
|------|--------------|-------------|
| Get started quickly | [Quick Start](QUICK_START.md) | - |
| Generate questions from file | [Quick Start](QUICK_START.md) | `01_question_generation.py` |
| Generate questions from text | [Quick Start](QUICK_START.md) | `generate_single_question()` |
| Understand all scripts | [Scripts Guide](SCRIPTS_GUIDE.md) | - |
| Compare models for question generation | [Scripts Guide](SCRIPTS_GUIDE.md) | `evaluate_models.py` |
| Test how well models answer questions | [Scripts Guide](SCRIPTS_GUIDE.md) | `test_model_answers.py` |
| Learn evaluation best practices | [Evaluation Guide](EVALUATION.md) | - |
| Understand the architecture | [Solution Overview](SOLUTION_OVERVIEW.md) | - |
| Use in Jupyter | [Quick Start](QUICK_START.md) | `examples/notebooks/*.py` |
| See complete workflow | - | `examples/complete_workflow.py` |

---

## 📁 Files Overview

### Documentation (`docs/`)
```
docs/
├── INDEX.md              # This file - documentation index
├── QUICK_START.md        # Start here - 5 min guide
├── SCRIPTS_GUIDE.md      # All scripts explained
├── EVALUATION.md         # Evaluation workflows
└── SOLUTION_OVERVIEW.md  # Architecture reference
```

### Scripts (`scripts/`)
```
scripts/
├── evaluate_models.py       # Evaluate question generation quality
└── test_model_answers.py    # Test how well models answer questions
```

### Examples (`examples/`)
```
examples/
├── complete_workflow.py             # Complete end-to-end example
└── notebooks/
    ├── 01_question_generation.py   # Interactive question generation
    └── 02_model_evaluation.py      # Interactive model testing
```

---

## 🎯 Learning Path

### Beginner Path
1. Read [Quick Start Guide](QUICK_START.md)
2. Run `examples/complete_workflow.py`
3. Try generating questions from your own content
4. Read [Scripts Guide](SCRIPTS_GUIDE.md) when you need more control

### Researcher Path
1. Read [Quick Start Guide](QUICK_START.md)
2. Read [Evaluation Guide](EVALUATION.md)
3. Use `examples/notebooks/*.py` for experiments
4. Read [Scripts Guide](SCRIPTS_GUIDE.md) for automation

### Developer Path
1. Read [Solution Overview](SOLUTION_OVERVIEW.md)
2. Read [Quick Start Guide](QUICK_START.md)
3. Explore API at http://localhost:8000/docs
4. Read [Scripts Guide](SCRIPTS_GUIDE.md) for CLI usage

---

## 💡 Key Concepts

### Two Evaluation Systems

**1. Question Generation Quality** (`evaluate_models.py`)
- Evaluates how well models **generate** questions
- Metrics: answerability, coherence, difficulty distribution
- Use when: Choosing the best model for question generation

**2. Model Answer Performance** (`test_model_answers.py`)
- Evaluates how well models **answer** questions
- Metrics: accuracy, AI-pass rate
- Use when: Testing if questions are AI-resistant

### Two Ways to Generate Questions

**From File** (Markdown)
```python
exam = generate_exam("content.md", total_questions=10)
```

**From Text** (No file)
```python
question = generate_single_question(
    "Your content here...",
    question_type="single_choice"
)
```

### Two Providers

**OpenAI GPT**
- Models: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- Setup: `OPENAI_API_KEY` in .env

**Yandex GPT**
- Models: yandexgpt, yandexgpt-lite
- Setup: `YANDEX_CLOUD_API_KEY`, `YANDEX_FOLDER_ID` in .env

---

## 🔄 Common Workflows

### Workflow 1: Generate & Evaluate Quality
```bash
# Generate with one model
curl -X POST http://localhost:8000/api/generate -d @config.json

# Compare generation quality
python scripts/evaluate_models.py --models gpt-4o-mini,gpt-4o --content file.md
```

### Workflow 2: Generate & Test Models
```bash
# Generate exam
python examples/complete_workflow.py

# Test models on exam
python scripts/test_model_answers.py --exam data/out/exam_*.json --compare
```

### Workflow 3: Research in Jupyter
```python
# Generate questions
%run examples/notebooks/01_question_generation.py

# Test models
%run examples/notebooks/02_model_evaluation.py
```

---

## 🆘 Getting Help

1. **Check the guides**:
   - [Quick Start](QUICK_START.md) for immediate examples
   - [Scripts Guide](SCRIPTS_GUIDE.md) for tool explanations
   - [Evaluation Guide](EVALUATION.md) for methodology

2. **Run examples**:
   ```bash
   python examples/complete_workflow.py
   ```

3. **Check tests**:
   ```bash
   pytest tests/ -v
   ```

4. **Report issues**:
   - https://github.com/TohaRhymes/llm_tester/issues

---

## 📝 Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| INDEX.md | ✅ Current | 2025-12-02 |
| QUICK_START.md | ✅ Current | 2025-12-02 |
| SCRIPTS_GUIDE.md | ✅ Current | 2025-12-02 |
| EVALUATION.md | ✅ Current | 2025-12-02 |
| SOLUTION_OVERVIEW.md | ✅ Current | 2025-12-02 |

---

## 🚀 Quick Start

New to the project? Run this:

```bash
# 1. Setup
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# 2. Run complete example
python examples/complete_workflow.py

# 3. Explore generated files
ls data/out/      # Exams
ls data/results/  # Evaluation results
```

Then read [Quick Start Guide](QUICK_START.md) for details!
