# LLM Test Generator

FastAPI service that generates educational exams from Markdown content and evaluates how well different LLM models answer questions. Supports OpenAI GPT and Yandex GPT for both question generation and answer evaluation.

## Quick Start
- Requirements: Python 3.11+, `pip`, OpenAI API key.
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Configure `.env` (create if missing):
  ```env
  # OpenAI configuration
  OPENAI_API_KEY=sk-...
  OPENAI_MODEL=gpt-4o-mini     # optional override
  OPENAI_BASE_URL=             # optional, for proxies/self-hosted endpoints

  # Provider selection
  DEFAULT_PROVIDER=openai       # openai | yandex | local (stub)

  # Yandex Cloud configuration (optional, for Yandex models)
  YANDEX_CLOUD_API_KEY=AQVN...
  YANDEX_CLOUD_API_KEY_IDENTIFIER=ajei...
  YANDEX_FOLDER_ID=b1g...

  OUTPUT_DIR=data/out          # where exams/grades are stored (default under data/)
  ```
- Run the API + static UI (creates data folders under `data/`):
  ```bash
  uvicorn app.main:app --reload
  ```
- Open http://localhost:8000 (UI) or http://localhost:8000/docs (Swagger).

## API Overview
- `GET /health` — service liveness.
- `POST /api/generate` — generate an exam from Markdown (`markdown_content` + optional `config` supporting counts or ratios, difficulty, language, seed, provider/model_name). Persists to `data/out/exam_<id>.json`.
- `POST /api/grade` — grade answers for an `exam_id`; multiple choice graded locally with partial credit, open-ended graded via LLM. Persists to `data/out/grade_<id>.json`.
- `POST /api/exams/import` — import a user-supplied exam JSON and store it under `data/out/`.
- `POST /api/upload` — upload `.md` into `data/uploads/`.
- `GET /api/files` and `GET /api/files/{filename}` — list/read uploaded Markdown.
- `GET /api/exams` and `GET /api/exams/{exam_id}` — list/read generated exams.
- Docs at `/docs`, `/redoc`, OpenAPI at `/openapi.json`.

## Docker
- Build: `docker build -t llm-tester .`
- Run: `docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data llm-tester` (override port via `-p 9000:8000` or set `PORT` in `.env`)
- Environment: set `OPENAI_API_KEY` or `DEFAULT_PROVIDER=local` for stubbed mode; `DATA_DIR/OUTPUT_DIR/UPLOADS_DIR` are respected inside the container.

### Docker Compose
- `docker-compose up --build` to start the API with data volume mounted (`./data -> /app/data`) and env from `.env`. Override port via `PORT` in `.env` (default 8000).
- Logs: streamed to stdout; view with `docker logs <container>` or `docker-compose logs -f`.

## Typical Flows
- Generate via API:
  ```bash
  curl -X POST http://localhost:8000/api/generate \
    -H "Content-Type: application/json" \
    -d '{"markdown_content":"# Topic\n## Section\nText", "config":{"total_questions":5,"single_choice_ratio":0.6,"multiple_choice_ratio":0.2,"open_ended_ratio":0.2}}'
  ```
- Grade answers:
  ```bash
  curl -X POST http://localhost:8000/api/grade \
    -H "Content-Type: application/json" \
    -d '{"exam_id":"ex-xxxxxx","answers":[{"question_id":"q-001","choice":[1]}]}'
  ```
- Use the UI: browse to `/` and follow upload → generate → take exam → grade.
- Postman: import `docs/api/LLM_Test_Generator.postman_collection.json` for a ready-made request set.

## Project Structure
```
app/
  main.py           # FastAPI bootstrap, routers, static mount
  api/              # REST endpoints (generate, grade, files, health)
  core/             # Parser, generator, grader, evaluator, RAG placeholder
  models/           # Pydantic schemas for API contracts
  services/         # LLM client wrappers (OpenAI, YandexGPT)
    openai_client.py     # OpenAI API wrapper
    yandex_client.py     # YandexGPT API wrapper
    model_answer_tester.py  # Model answer evaluation service
static/             # Bundled frontend served from /
data/               # Runtime root for generated artifacts
  uploads/          # Uploaded Markdown files
  out/              # Generated exams and grading outputs
scripts/
  evaluate_models.py       # Question generation quality benchmarking
  test_model_answers.py    # Model answer evaluation CLI
examples/notebooks/        # Jupyter-friendly examples
  01_question_generation.py  # Generate questions from content
  02_model_evaluation.py     # Test models on exams
tests/              # unit/integration/BDD suites
docs/
  ARCHITECTURE.md        # System architecture, API reference, frontend design
  PROJECT_STATUS.md      # Project status, results, and roadmap
  CONTRIBUTING.md        # TDD/BDD workflow and guidelines
  SECURITY.md            # Security policy
  CHANGELOG.md           # Version history and migration guides
  RESEARCH_DECK.md       # Research presentation (Russian)
  archive/               # Historical documents (PLAN.md, RESEARCH_RESULTS.md, AUDIT_REPORT.md)
```

## Testing and Evaluation

### Automated Tests
```bash
pytest tests/ -v                    # Run all unit tests
behave tests/bdd/features/          # Run BDD scenarios
pytest --cov=app --cov-report=html  # Generate coverage report
```
Coverage HTML reports are written to `data/htmlcov/`.

### Question Generation Quality Evaluation
Benchmark different LLMs for question generation:
```bash
python scripts/evaluate_models.py \
  --models gpt-4o-mini,gpt-4o \
  --content docs/examples/sample_data/sample_medical.md \
  --num-questions 10
```

### Model Answer Evaluation
Test how well models answer exam questions:
```bash
# Test single model
python scripts/test_model_answers.py \
  --exam data/out/exam_ex-123.json \
  --model gpt-4o-mini \
  --provider openai

# Compare multiple models
python scripts/test_model_answers.py \
  --exam data/out/exam_ex-123.json \
  --compare
```

### Jupyter-Friendly Examples
```python
# Generate questions
from examples.notebooks.question_generation import generate_exam, save_exam

exam = generate_exam("content.md", total_questions=20, language="ru")
exam_file = save_exam(exam)

# Test models
from examples.notebooks.model_evaluation import test_model, compare_models

result = test_model(exam_file, "gpt-4o-mini", "openai")
print(f"Accuracy: {result.accuracy:.2%}")

comparison = compare_models(
    exam_file,
    models=[
        {"model_name": "gpt-4o-mini", "provider": "openai"},
        {"model_name": "yandexgpt-lite", "provider": "yandex"}
    ]
)
```

## Python API Examples

### Generate a Single Question
```python
from app.core.exam_builder import generate_question

snippet = """
Гестационная гипертензия — это артериальное давление ≥140/90 мм рт. ст.,
впервые выявленное после 20-й недели беременности.
"""

question = generate_question(
    content=snippet,
    question_type="single_choice",
    difficulty="medium",
    provider="openai",
    language="ru"
)

print(question["stem"])
print(question["options"])
print(question["correct"])
```

### Generate an Exam from Text
```python
from app.core.exam_builder import generate_exam_from_text

content = """
# Topic
## Section
Text here...
"""

exam = generate_exam_from_text(
    markdown_content=content,
    total_questions=10,
    single_choice_ratio=0.6,
    multiple_choice_ratio=0.4,
    language="ru"
)
```

### Generate from File
```python
from app.core.exam_builder import generate_exam_from_file

exam = generate_exam_from_file(
    file_path="path/to/your/medical_content.md",
    total_questions=20,
    difficulty="mixed",
    language="ru"
)
```

### Save and Load Exams
```python
from app.core.exam_builder import save_exam, load_exam

path = save_exam(exam)
loaded_exam = load_exam(path)
```

### RAG Integration Pattern
```python
from app.core.exam_builder import generate_question

def generate_questions_from_rag(query, retrieved_snippets, num_questions=5):
    questions = []
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
```

## Frontend Architecture

The web UI has been completely refactored into a clean, modular architecture:

- **HTML**: Reduced from 879 to 170 lines (-81%)
- **CSS**: Extracted to `static/css/style.css` (225 lines)
- **JavaScript**: Modularized into 6 files (953 lines total):
  - `api-client.js` - Centralized API communication with APIError class
  - `ui-utils.js` - UI helpers, validation, and user-friendly error messages
  - `file-manager.js` - File upload and management
  - `exam-manager.js` - Exam generation and listing with pagination
  - `test-taker.js` - Test taking workflow and grading display
  - `main.js` - Application initialization

**Key Features**:
- Professional error handling (no more `alert()` calls)
- Input validation before API calls
- Loading states with spinners
- Smart error message mapping (HTTP codes → user-friendly text)
- Modular, maintainable, testable code

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for complete architecture documentation.

## 📚 Documentation

**Architecture & Development**:
- [Architecture](docs/ARCHITECTURE.md) - System architecture and design
- [Project Status](docs/PROJECT_STATUS.md) - Project status, research results, and roadmap
- [Research Deck](docs/RESEARCH_DECK.md) - Research presentation (Russian)

**Contributing & Security**:
- [Contributing Guide](docs/CONTRIBUTING.md) - TDD/BDD workflow and guidelines
- [Security Policy](docs/SECURITY.md) - Security measures and vulnerability reporting
- [Changelog](docs/CHANGELOG.md) - Version history and migration guides

## Notes
- OpenAI or Yandex API key required depending on provider choice
- If provider credentials are missing, the service falls back to a local stub LLM for development (set `DEFAULT_PROVIDER=local` explicitly for offline use)
- Generated exams run through a validator (schema sanity, source refs, deduplication, grounding overlap with source) before being returned; validation surfaces grounded ratio and section coverage
- CORS is configured via `CORS_ORIGINS` environment variable (defaults to localhost); there is no authentication - add auth middleware before production
- Exams/grades are stored on disk; clean up `data/out/` and `data/uploads/` as needed
- Validation failures trigger a few automatic regeneration attempts; if they persist, the API returns a generic validation error (check server logs for details)
