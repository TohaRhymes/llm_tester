# Jupyter Notebooks - Question Generation Examples

This directory contains interactive Jupyter notebooks demonstrating the LLM Test Generator.

## Available Notebooks

### `question_generation_examples.ipynb`
Comprehensive notebook with 10 examples covering:
- Single question generation from snippets
- Multiple-choice questions
- Multi-language support (Russian/English)
- Full exam generation
- RAG integration patterns
- Saving/loading exams
- Different difficulty levels
- Using OpenAI and YandexGPT providers

Perfect for your team to learn the API and test RAG integration.

## Quick Start

1. **Setup Environment:**
```bash
# From project root
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
jupyter notebook  # or jupyter lab
```

3. **Run Notebook:**
- Navigate to `examples/notebooks/`
- Open `question_generation_examples.ipynb`
- Run cells sequentially (Shift+Enter)

## Prerequisites

- Python 3.8+
- Jupyter Notebook or JupyterLab
- OpenAI API key (or YandexGPT credentials)
- Required packages from `requirements.txt`

## Environment Variables

Required in `.env` file:
```bash
# OpenAI (required for examples)
OPENAI_API_KEY=sk-proj-your-key-here

# Yandex (optional, for Example 10)
YANDEX_CLOUD_API_KEY=your-key
YANDEX_CLOUD_API_KEY_IDENTIFIER=your-identifier
YANDEX_FOLDER_ID=your-folder-id
```

## Troubleshooting

### "OPENAI_API_KEY not set in environment"

The notebook loads `.env` from the project root. Make sure:
1. `.env` file exists in `/home/toharhymes/work/itmo/llm_tester/`
2. Contains valid `OPENAI_API_KEY=sk-...`
3. Restart the Jupyter kernel after creating `.env`

### ModuleNotFoundError

Run from project root or ensure virtual environment is activated:
```bash
# Activate venv if using one
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Questions in wrong language

Check the `language` parameter in `generate_question()`:
- Use `language="ru"` for Russian
- Use `language="en"` for English

## Usage Patterns

### For RAG Pipelines

```python
from app.core.exam_builder import generate_question

# Your retrieved snippet
snippet = "Medical content from vector database..."

# Generate question
q = generate_question(
    content=snippet,
    question_type="single_choice",
    language="ru"
)
```

### For Batch Processing

```python
snippets = [...]  # Your RAG results
questions = [
    generate_question(s, question_type="single_choice", language="ru")
    for s in snippets
]
```

## Alternative: Python Script

If you prefer not to use notebooks, see:
- `examples/simple_generation_example.py` - Runnable Python script
- `examples/QUICK_START.md` - Quick reference guide

## Next Steps

1. Run all examples in the notebook
2. Try with your own medical content
3. Integrate into your RAG pipeline
4. Check `examples/QUICK_START.md` for API reference

## Support

- Main documentation: See project root README.md
- API details: See CLAUDE.md
- Issues: Report in project issue tracker
