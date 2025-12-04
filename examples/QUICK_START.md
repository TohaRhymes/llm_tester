# Quick Start Guide: Question Generation from MD Snippets

This guide shows you how to quickly generate questions from Markdown snippets for your RAG pipeline.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys in `.env` file:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Quick Examples

### 1. Generate a Single Question (Simplest)

```python
from app.core.exam_builder import generate_question

# Your MD snippet (from RAG retrieval)
snippet = """
Гестационная гипертензия — это артериальное давление ≥140/90 мм рт. ст.,
впервые выявленное после 20-й недели беременности.
"""

# Generate question
question = generate_question(
    content=snippet,
    question_type="single_choice",  # or "multiple_choice"
    difficulty="medium",            # "easy", "medium", or "hard"
    provider="openai",              # or "yandex"
    language="ru"                   # or "en"
)

# Use the question
print(question['stem'])           # Question text
print(question['options'])        # List of answer options
print(question['correct'])        # List of correct answer indices
```

### 2. Generate Multiple Questions from Text

```python
from app.core.exam_builder import generate_exam_from_text

content = """
# Your Markdown Content

## Section 1
Content here...

## Section 2
More content...
"""

exam = generate_exam_from_text(
    markdown_content=content,
    total_questions=10,
    single_choice_ratio=0.6,      # 60% single-choice
    multiple_choice_ratio=0.4,    # 40% multiple-choice
    language="ru"
)

# Access questions
for q in exam.questions:
    print(f"Q: {q.stem}")
    print(f"Type: {q.type}")
    print(f"Options: {q.options}")
    print(f"Correct: {q.correct}")
```

### 3. Generate from File

```python
from app.core.exam_builder import generate_exam_from_file

exam = generate_exam_from_file(
    file_path="path/to/your/medical_content.md",
    total_questions=20,
    difficulty="mixed",  # or "easy", "medium", "hard"
    language="ru"
)
```

### 4. Save and Load Exams

```python
from app.core.exam_builder import save_exam, load_exam

# Save
path = save_exam(exam)
print(f"Saved to: {path}")

# Load
loaded_exam = load_exam(path)
```

## RAG Integration Pattern

Here's how to use this in a RAG pipeline:

```python
from app.core.exam_builder import generate_question

def generate_questions_from_rag(query, retrieved_snippets, num_questions=5):
    """
    Generate questions from RAG-retrieved snippets.

    Args:
        query: User's search query
        retrieved_snippets: List of relevant text chunks from vector DB
        num_questions: Number of questions to generate

    Returns:
        List of generated questions
    """
    questions = []

    # Take top N snippets
    for snippet in retrieved_snippets[:num_questions]:
        question = generate_question(
            content=snippet,
            question_type="single_choice",
            difficulty="medium",
            provider="openai",
            language="ru"
        )
        questions.append(question)

    return questions

# Example usage
query = "преэклампсия диагностика"
snippets = [
    "Преэклампсия диагностируется при АД ≥140/90...",
    "Критерии тяжелой преэклампсии включают...",
    # ... more snippets from your vector DB
]

questions = generate_questions_from_rag(query, snippets, num_questions=3)
```

## API Reference

### `generate_question(content, **kwargs)`

Generate a single question from text.

**Parameters:**
- `content` (str): Text content to generate question from
- `question_type` (str): "single_choice", "multiple_choice", or "open_ended"
- `difficulty` (str): "easy", "medium", or "hard"
- `provider` (str): "openai" or "yandex"
- `model_name` (str, optional): Override default model
- `language` (str): "ru" or "en"

**Returns:** Dictionary with:
```python
{
    'id': 'q-xxx',
    'type': 'single_choice',
    'stem': 'Question text',
    'options': ['Option 1', 'Option 2', ...],
    'correct': [0],  # indices of correct answers
    'meta': {'difficulty': 'medium', ...}
}
```

### `generate_exam_from_text(markdown_content, **kwargs)`

Generate multiple questions from Markdown text.

**Parameters:**
- `markdown_content` (str): Markdown content
- `total_questions` (int): Number of questions to generate (default: 10)
- `single_choice_ratio` (float): Ratio of single-choice questions (default: 0.5)
- `multiple_choice_ratio` (float): Ratio of multiple-choice (default: 0.3)
- `open_ended_ratio` (float): Ratio of open-ended (default: 0.2)
- `difficulty` (str): "easy", "medium", "hard", or "mixed" (default: "mixed")
- `language` (str): "ru" or "en" (default: "en")
- `seed` (int, optional): Random seed for reproducibility

**Returns:** `Exam` object with `.questions` list

### `generate_exam_from_file(file_path, **kwargs)`

Generate exam from Markdown file. Same parameters as `generate_exam_from_text()`.

### `save_exam(exam, output_file=None)`

Save exam to JSON file.

**Parameters:**
- `exam`: Exam object
- `output_file` (str, optional): Output path (default: auto-generated)

**Returns:** Path to saved file

### `load_exam(exam_path)`

Load exam from JSON file.

**Parameters:**
- `exam_path` (str): Path to exam JSON file

**Returns:** `Exam` object

## Question Object Structure

```python
question = {
    'id': 'q-001',
    'type': 'single_choice',  # or 'multiple_choice', 'open_ended'
    'stem': 'What is the diagnostic criterion for gestational hypertension?',
    'options': [
        'BP ≥140/90 mmHg',
        'BP ≥130/80 mmHg',
        'BP ≥160/100 mmHg',
        'BP ≥150/95 mmHg'
    ],
    'correct': [0],  # Zero-indexed! First option is correct
    'source_refs': ['section-1', 'page-3'],
    'meta': {
        'difficulty': 'medium',
        'tags': ['hypertension', 'diagnosis']
    }
}
```

## Exam Object Structure

```python
exam = {
    'exam_id': 'ex-abc123',
    'questions': [
        {...},  # Question objects
        {...},
    ],
    'config_used': {
        'total_questions': 10,
        'language': 'ru',
        # ... other config
    }
}
```

## Common Issues

### Issue: "OPENAI_API_KEY not set in environment"

**Solution:**
1. Copy `.env.example` to `.env`
2. Add your OpenAI API key: `OPENAI_API_KEY=sk-...`
3. Reload environment or restart

### Issue: Questions in wrong language

**Solution:** Set `language` parameter:
```python
generate_question(content, language="ru")  # for Russian
generate_question(content, language="en")  # for English
```

### Issue: Need deterministic question generation

**Solution:** Use `seed` parameter:
```python
generate_exam_from_text(content, seed=42)
```

### Issue: Want to use YandexGPT instead of OpenAI

**Solution:**
1. Configure Yandex credentials in `.env`:
```
YANDEX_CLOUD_API_KEY=your-key
YANDEX_CLOUD_API_KEY_IDENTIFIER=your-identifier
YANDEX_FOLDER_ID=your-folder-id
```
2. Use `provider="yandex"`:
```python
generate_question(content, provider="yandex")
```

## Example Workflows

### Workflow 1: Simple Single Question

```python
from app.core.exam_builder import generate_question

snippet = "Your medical text here..."
q = generate_question(snippet, question_type="single_choice", language="ru")
print(q['stem'])
```

### Workflow 2: Batch Generation from Multiple Snippets

```python
from app.core.exam_builder import generate_question

snippets = ["Snippet 1...", "Snippet 2...", "Snippet 3..."]
questions = [
    generate_question(s, question_type="single_choice", language="ru")
    for s in snippets
]
```

### Workflow 3: Full Exam with Custom Config

```python
from app.core.exam_builder import ExamBuilder

builder = ExamBuilder()
exam = builder.from_text(
    markdown_content=content,
    total_questions=20,
    single_choice_ratio=0.7,
    multiple_choice_ratio=0.3,
    difficulty="hard",
    language="ru",
    exam_id="custom-exam-001"
)
builder.save(exam, "my_exam.json")
```

## Next Steps

1. **Jupyter Notebook**: See `examples/notebooks/question_generation_examples.ipynb` for interactive examples
2. **Python Script**: See `examples/simple_generation_example.py` for a complete script
3. **API Documentation**: Check the main README.md for full API details
4. **Integration**: Read CLAUDE.md for integration patterns

## Support

- Issues: https://github.com/your-repo/issues
- Documentation: See `/docs` folder
- Examples: See `/examples` folder
