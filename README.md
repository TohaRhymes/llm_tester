# LLM Test Generator

AI-powered test generation system for educational materials. Generate and grade exams (single-choice, multiple-choice, and open-ended questions) from Markdown content using OpenAI.

## Quick Start

### 1. Install

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### 2. Run

```bash
python3 -m uvicorn app.main:app --reload
```

Open: http://localhost:8000 (Web UI) or http://localhost:8000/docs (API)

### 3. Use

**Web Interface:**
1. Upload Markdown files
2. Generate exam (configure question count, types, difficulty)
3. View questions with answers
4. Take test and get instant grading

**API:**
```bash
# Generate exam with open-ended questions
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "# Topic\n## Section\nContent here...",
    "config": {
      "total_questions": 10,
      "single_choice_ratio": 0.5,
      "multiple_choice_ratio": 0.3,
      "open_ended_ratio": 0.2
    }
  }'

# Grade answers (choice + text)
curl -X POST http://localhost:8000/api/grade \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": "ex-abc123",
    "answers": [
      {"question_id": "q-001", "choice": [1]},
      {"question_id": "q-002", "text_answer": "Preeclampsia involves endothelial dysfunction..."}
    ]
  }'
```

## Features

- **Question Generation**: Single-choice, multiple-choice, and open-ended questions from Markdown
- **Automated Grading**: With partial credit support and AI-powered open-ended grading
- **Source Traceability**: Every question links to source material
- **AI Feedback**: Detailed rubric-based feedback for open-ended responses
- **Medical Focus**: Optimized for medical education content
- **Web UI**: Complete workflow from upload to grading
- **REST API**: Full Swagger documentation at `/docs`

## Project Structure

```
llm_tester/
├── app/
│   ├── api/              # FastAPI endpoints (8 endpoints)
│   │   ├── generate.py   # POST /api/generate
│   │   ├── grade.py      # POST /api/grade
│   │   ├── files.py      # Upload/list files, exams
│   │   └── health.py     # GET /health
│   ├── core/             # Business logic
│   │   ├── parser.py     # Markdown parsing
│   │   ├── generator.py  # Question generation
│   │   └── grader.py     # Answer grading
│   ├── models/           # Pydantic schemas
│   ├── services/         # OpenAI client
│   └── main.py           # FastAPI app
├── tests/
│   ├── unit/             # Unit tests (72 tests)
│   ├── integration/      # API tests (11 tests)
│   └── bdd/              # BDD scenarios (12 scenarios)
├── docs/                 # Documentation
│   ├── PRESENTATION.md   # Exam defense presentation
│   ├── AUTOMATED_REVIEW.md  # Verification checklist
│   └── description.md    # Technical description
├── examples/             # Sample medical content
├── static/               # Web UI
└── out/                  # Generated exams
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/generate` | Generate exam from Markdown |
| POST | `/api/grade` | Grade student answers |
| POST | `/api/upload` | Upload Markdown file |
| GET | `/api/files` | List uploaded files |
| GET | `/api/files/{filename}` | Get file content |
| GET | `/api/exams` | List generated exams |
| GET | `/api/exams/{exam_id}` | Get specific exam |

Full API documentation: http://localhost:8000/docs (when server is running)

### Postman Collection

Import the Postman collection for quick API testing:

1. **Import**: `LLM_Test_Generator.postman_collection.json`
2. **Configure**: Variables are pre-set (`base_url`, `exam_id`, `uploaded_filename`)
3. **Run**: Execute requests in order for complete workflow

**Collection includes:**
- All 8 API endpoints with example requests
- Automated tests for response validation
- Environment variables auto-populated from responses
- Pre-request scripts for dynamic data

**Complete workflow test:**
1. Health Check → verify API is running
2. Upload File → upload sample medical content
3. Generate Exam → create 5-question exam
4. Get Exam → retrieve generated exam
5. Grade Exam → evaluate sample answers

All requests include automated tests that validate:
- Response status codes
- Response structure and required fields
- Data types and constraints

## Testing

```bash
# Run all tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# BDD scenarios
behave tests/bdd/features/

# Coverage report
pytest --cov=app --cov-report=html tests/
```

**Test Results:**
- 81/82 tests passing (99%)
- 80% code coverage
- 12 BDD scenarios
- TDD approach (tests-first development)

## Configuration

Edit `.env`:

```env
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Defaults
DEFAULT_TOTAL_QUESTIONS=20
DEFAULT_SINGLE_CHOICE_RATIO=0.7
DEFAULT_MULTIPLE_CHOICE_RATIO=0.3
OUTPUT_DIR=out
```

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **AI**: OpenAI API (gpt-4o-mini)
- **Testing**: pytest, behave (BDD), httpx
- **Validation**: Pydantic v2
- **Parsing**: markdown-it-py

## Documentation

- **Quick Start**: This README
- **API Reference**: http://localhost:8000/docs (Swagger)
- **Model Evaluation**: [docs/EVALUATION.md](docs/EVALUATION.md) - Compare LLM models
- **Technical Details**: [docs/description.md](docs/description.md)
- **Exam Defense**: [docs/PRESENTATION.md](docs/PRESENTATION.md)
- **Verification**: [docs/AUTOMATED_REVIEW.md](docs/AUTOMATED_REVIEW.md)

## Development

This project follows **Test-Driven Development (TDD)** and **Behavior-Driven Development (BDD)**:

1. Tests written before implementation
2. RED → GREEN → REFACTOR cycle
3. BDD scenarios for user-facing features
4. 80%+ code coverage requirement

See [docs/description.md](docs/description.md) for architecture details.

## License

Educational project for ITMO University.

## Support

- GitHub Issues: https://github.com/TohaRhymes/llm_tester/issues
- API Docs: http://localhost:8000/docs
- Verification: [docs/AUTOMATED_REVIEW.md](docs/AUTOMATED_REVIEW.md)
