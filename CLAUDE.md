# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLM-based test generator for medical education materials. The system ingests Markdown files with educational content and generates multiple-choice exams with automated grading.

**Core Functionality:**
- Input: One or more Markdown files (medical/educational content)
- Output 1: Generated exam (single/multiple choice questions)
- Output 2: Automated answer grading against answer keys

## Tech Stack

- **Backend**: Python + FastAPI (with Swagger/OpenAPI), uvicorn
- **Testing**: pytest (unit/integration) → behave (BDD scenarios)
- **AI Integration**: OpenAI API (chat completion + embeddings for RAG)
- **Storage**: File-based (no database in MVP)
- **Configuration**: YAML configs, .env for secrets

## Development Commands

### Environment Setup
```bash
# Install dependencies (once requirements.txt is created)
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Server
```bash
# Start development server
uvicorn app.main:app --reload

# Access Swagger UI
# Navigate to http://localhost:8000/docs
```

### Testing
```bash
# Run all unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_qgen.py -v

# Run BDD scenarios
behave tests/bdd/features/

# Run specific feature
behave tests/bdd/features/generate_questions.feature

# Run tests with coverage
pytest --cov=app --cov-report=html tests/
```

## Architecture

### Directory Structure
```
/app
  /api                    # FastAPI endpoints
    generate.py          # POST /api/generate - exam generation
    grade.py             # POST /api/grade - answer grading
    files.py             # POST /api/upload, GET /api/files
    exams.py             # GET /api/exams, POST /api/exams/import
    health.py            # GET /health
  /core                   # Core business logic
    md_ingest.py         # Markdown parser → sections/chunks
    chunker.py           # Text chunking with metadata
    retriever.py         # Simple RAG retrieval + embeddings
    qgen.py              # Question generation (MCQ/SCQ)
    grader.py            # Answer validation against keys
    exam_builder.py      # Exam construction and validation
  /models                 # Pydantic schemas
    schemas.py           # API contracts and data models
  /services
    openai_client.py     # OpenAI API wrapper (chat + embeddings)
    yandex_client.py     # YandexGPT API wrapper
    model_answer_tester.py  # Model answer evaluation
  /utils
    path.py              # File operations with path safety
/static                   # Frontend (modular architecture)
  index.html             # 170 lines - Clean HTML structure
  /css
    style.css            # 225 lines - Extracted styles
  /js                    # 953 lines total - 6 modules
    api-client.js        # API communication with APIError class
    ui-utils.js          # UI helpers, validation, error messages
    file-manager.js      # File upload and management
    exam-manager.js      # Exam generation and listing
    test-taker.js        # Test taking and grading
    main.js              # Application initialization
/data                     # Runtime data (not in git)
  /uploads               # Uploaded Markdown files
  /out                   # Generated exams and grading outputs
/tests
  /unit                  # pytest unit tests (TDD approach)
    test_security.py     # Security-specific tests (CORS, file limits, etc.)
  /integration           # End-to-end API tests
  /bdd
    /features            # Gherkin .feature files
    /steps               # Step definitions
/docs                     # Documentation
  ARCHITECTURE.md        # System architecture, API reference, frontend design
  PLAN.md                # Development roadmap
  QUICK_START.md         # 5-minute setup guide
  CONTRIBUTING.md        # Contribution guidelines
  SECURITY.md            # Security policy
  CHANGELOG.md           # Version history
  AUDIT_REPORT.md        # Project audit
/examples
  /notebooks             # Jupyter-friendly examples
    01_question_generation.py
    02_model_evaluation.py
  complete_workflow.py   # End-to-end example script
  test_open_ended_api.sh # API testing script
/scripts
  evaluate_models.py     # Question generation benchmarking
  test_model_answers.py  # Model answer evaluation CLI
```

### Key Components

**Markdown Ingestion Pipeline** (app/core/md_ingest.py → app/core/chunker.py):
- Parses Markdown into structured sections (headings, paragraphs, lists, tables)
- Chunks content with configurable size and overlap
- Maintains source references for traceability

**RAG Retrieval** (app/core/retriever.py):
- Optional embeddings-based context retrieval
- Uses OpenAI text-embedding-3-small
- Returns top-k most relevant chunks for each question

**Question Generator** (app/core/qgen.py):
- Generates single_choice and multiple_choice questions
- Configurable difficulty levels and type distribution
- Includes source references linking questions to source material
- Optional deduplication and answerability validation

**Grader** (app/core/grader.py):
- Validates answers against correct indices
- Supports partial credit for multiple_choice questions
- Returns per-question and summary results

**Frontend Architecture** (static/):
- **Modular JavaScript**: 6 separate modules with clear responsibilities
- **api-client.js**: Centralized API communication with custom APIError class
- **ui-utils.js**: Reusable UI helpers, validation, and smart error messages
- **file-manager.js**: File upload and management operations
- **exam-manager.js**: Exam generation, listing, and pagination
- **test-taker.js**: Test taking workflow and grading display
- **main.js**: Application initialization and tab management
- **Professional UX**: Loading states, input validation, user-friendly error messages
- **No alert() calls**: All feedback through consistent UI components
- **Error Mapping**: HTTP status codes → user-friendly messages (413 → "File too large. Maximum size is 10MB.")

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for complete architecture documentation.

### API Contracts

**POST /api/generate**
```json
{
  "config_yaml": "<yaml-string>",
  // OR
  "config": { /* inline config object */ }
}
```
Returns: Exam object with questions, exam_id, and config_used

**POST /api/grade**
```json
{
  "exam_id": "ex-123",
  "answers": [
    {"question_id": "q-001", "choice": [2]}
  ]
}
```
Returns: GradeResponse with summary and per_question results

### Data Models (Pydantic Schemas)

**Question**:
- id, type (single_choice | multiple_choice)
- stem (question text)
- options (array of answer choices)
- correct (array of correct indices)
- source_refs (traceability to source material)
- meta (difficulty, tags)

**Exam**:
- exam_id, questions array, config_used

**GradeResponse**:
- summary (total, correct, score_percent)
- per_question breakdown

## Configuration

Default config location: `examples/config.example.yaml`

Key configuration sections:
- **input**: files list, language
- **generation**: total_questions, type distribution (single_choice/multiple_choice ratios), difficulty, seed
- **rag**: enabled flag, chunk_size, chunk_overlap, top_k, embeddings model
- **sources**: include_headings/exclude_headings filters
- **grading**: partial_credit_for_multiple_choice
- **export**: output directory and format

Environment variables (.env):
- OPENAI_API_KEY (required)
- OPENAI_BASE (optional, for custom endpoints)
- GIT_USER, GIT_EMAIL, GITHUB_TOKEN (for autocommit feature)

## Development Approach

**Tests-First (TDD → BDD)**:
1. Write failing unit tests first
2. Implement minimal code to pass tests
3. Write BDD scenarios for user-facing behavior
4. All features must have corresponding tests before implementation

**Test Coverage Requirements**:
- Minimum 80% code coverage
- All core modules (md_ingest, chunker, qgen, grader) must have comprehensive unit tests
- Integration tests for both API endpoints

**Auto-commit Strategy**:
- Successful `/generate` call → commits exam output to `out/exam_{id}.json`
- Successful `/grade` call → commits grade report to `out/grade_{id}.json`
- Uses conventional commit format: `feat(generate): exam ex-123 (20q)`

## Important Implementation Notes

**Question Generation**:
- Use seed for deterministic generation in tests
- Validate that each question has 3-5 options
- Ensure no empty options
- Verify source_refs are present and valid
- For single_choice: exactly one correct answer
- For multiple_choice: at least one correct answer

**Grading Logic**:
- single_choice: exact match required
- multiple_choice: partial credit optional (configurable)
- Always return both summary stats and per-question breakdown

**Security Considerations**:
- Never commit .env file (contains API keys)
- **CORS**: Configured via `CORS_ORIGINS` environment variable (defaults to localhost, not wildcard)
- **File Upload Limits**: 10MB maximum file size enforced
- **Path Traversal**: All file paths validated using safe_join utility
- **Rate Limiting**: Implemented using slowapi (configurable per endpoint)
- **MD5 Usage**: All hashlib.md5 calls use `usedforsecurity=False` flag
- Sanitize user inputs in config parsing
- Security tests in tests/unit/test_security.py verify all protections
- See [docs/SECURITY.md](docs/SECURITY.md) for complete security policy and audit results

## Medical Content Context

Sample content focuses on obstetrics/gynecology topics (e.g., gestational hypertension, preeclampsia). Questions should:
- Test clinical knowledge and decision-making
- Include diagnostic criteria and management principles
- Reference specific medical values/thresholds from source material
- Avoid ambiguous or trick questions

## Testing Medical Question Quality

When generating questions, validate:
- Answerability: Can the question be answered from the provided context?
- Unambiguity: Is there a clear correct answer?
- Clinical relevance: Does the question test meaningful knowledge?
- Distractor quality: Are incorrect options plausible but clearly wrong?
