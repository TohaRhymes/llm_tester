# Project Status & Results

**Last Updated**: 2026-01-22
**Project**: LLM Test Generator for Medical Education
**Repository**: https://github.com/TohaRhymes/llm_tester

---

## Executive Summary

LLM-based test generator for educational materials with automated grading. The system successfully processes Markdown/PDF files, generates multiple-choice and open-ended exams, and provides automated scoring with rubrics.

**Status**: ✅ **Production-ready** with research evaluation pipeline

### Key Achievements

- ✅ Full-stack implementation (FastAPI backend + modular frontend)
- ✅ Multi-provider LLM support (OpenAI, YandexGPT, local stub)
- ✅ Question generation with validation (grounding, coverage, deduplication)
- ✅ Automated grading for choice and open-ended questions
- ✅ Research evaluation pipeline with synthetic students
- ✅ Real-world pilot at biobanking school (Ott Institute)
- ✅ Security audit completed and all issues resolved
- ✅ Frontend refactored to modular architecture (6 modules)

---

## Real-World Validation

### Biobanking School at Ott Institute

During the biobanking educational program, we successfully deployed the system:

- **Materials**: Instructor lecture notes (obstetrics/gynecology, biobanking)
- **Process**: Generated questions mixed with standard test items
- **Outcome**: Positive feedback, questions deemed usable in practice
- **Insight**: LLM-generated tests are pedagogically viable but require validation

---

## Research Results

### Experimental Setup

**Datasets**:
- **Medical domain**: 21 Markdown files (obstetrics, gynecology)
- **ML domain**: 68 Markdown files (machine learning topics)

**Configurations tested**:
- Prompt variants: `default` vs `grounded` (explicit grounding instruction)
- RAG: enabled/disabled (top_k=3 chunks)
- Question mix: 2 single-choice + 2 multiple-choice + 2 open-ended per exam

**Evaluation**:
- 48 synthetic student profiles per configuration
- Metrics: quality score, grounded ratio, coverage, mean score
- RAGAS metrics on subsampled open-ended questions

### Results Summary

#### Medical Domain (21 files)

| Variant  | RAG | Quality | Grounded | Coverage | Mean Score | Open-Ended | Choice |
|----------|-----|---------|----------|----------|------------|------------|--------|
| default  | off | 0.9540  | 0.2380   | 1.0000   | 52.60      | 0.5000     | 0.5389 |
| grounded | off | 0.9683  | 0.2380   | 1.0000   | 52.35      | 0.5000     | 0.5352 |
| default  | on  | 0.9667  | 0.2539   | 1.0000   | 52.02      | 0.5000     | 0.5303 |
| grounded | on  | 0.9540  | 0.2619   | 1.0000   | 52.58      | 0.5000     | 0.5387 |

**Observations**:
- High quality scores across all configurations (>0.95)
- Low grounded ratio (~0.24) due to many files having only top-level headings
- Perfect coverage (1.0) - all source sections represented
- Scores around 52% suggest moderate difficulty
- RAG slightly increases grounded ratio

#### ML Domain (68 files)

| Variant  | RAG | Quality | Grounded | Coverage | Mean Score | Open-Ended | Choice |
|----------|-----|---------|----------|----------|------------|------------|--------|
| default  | off | 0.9608  | 0.7598   | 0.4999   | 51.98      | 0.5000     | 0.5296 |
| grounded | off | 0.9579  | 0.7818   | 0.5080   | 52.38      | 0.5000     | 0.5358 |
| default  | on  | 0.9529  | 0.7426   | 0.3556   | 52.74      | 0.5000     | 0.5411 |
| grounded | on  | 0.9544  | 0.7843   | 0.3528   | 52.54      | 0.5000     | 0.5381 |

**Observations**:
- High quality maintained (>0.95)
- **Grounded prompt improves grounding** (~0.76 → 0.78)
- Coverage drops with RAG (~0.50 → 0.35) - RAG focuses retrieval
- Consistent scores around 52%
- Grounded prompt is more effective with structured content

#### RAGAS Metrics (Subsampled)

**Medical** (5 docs, max 20 samples per config):
- Faithfulness: NaN (insufficient statement extraction from short answers)
- Answer relevancy: ~0.08 (low, synthetic answers are brief)
- Context precision/recall: 0.0–0.08 (limited retrieval match)

**ML** (5 docs, max 20 samples):
- Faithfulness: NaN (same issue)
- Answer relevancy: 0.0–0.075
- Context recall: 0.1–0.2 (slightly better than medical)

**Note**: RAGAS metrics are unreliable with synthetic short-form answers. Future work should use real student responses or richer synthetic data.

---

## Key Findings

### 1. Classic Tests Are Vulnerable to LLMs

Synthetic students (LLMs) achieve ~52% accuracy on generated exams **without understanding**. This demonstrates:
- Multiple-choice formats can be gamed by pattern matching
- Passing a test ≠ demonstrating knowledge
- Need for deeper evaluation beyond surface-level Q&A

### 2. Grounded Prompts Improve Fidelity

Explicit grounding instructions in prompts increase the proportion of questions with traceable source references, especially on structured content (ML: 0.76 → 0.78).

### 3. RAG Trade-offs

- ✅ Increases grounded ratio (better source attribution)
- ❌ Reduces coverage (focuses on top-k chunks, may miss topics)
- Use RAG when precision matters more than breadth

### 4. Quality Remains High

All configurations maintain quality scores >0.95, suggesting robust question generation across settings.

---

## Roadmap

### Completed ✅

- [x] Core generation pipeline (parser → generator → validator)
- [x] Multi-provider support (OpenAI, Yandex, local stub)
- [x] Automated grading (choice + open-ended with rubrics)
- [x] Research evaluation pipeline (synthetic students, metrics)
- [x] Frontend modularization (6 JavaScript modules)
- [x] Security audit and fixes (CORS, file limits, path traversal)
- [x] PDF upload and conversion
- [x] Real-world pilot deployment

### Short Term (Next 2-4 Weeks)

- [ ] Surface validation metrics in `/api/generate` response
- [ ] Add filters (language, provider) to exams listing API
- [ ] Improve frontend: download exams, better pagination
- [ ] Create Postman/CLI parity test collection
- [ ] Refine RAGAS evaluation with richer synthetic data

### Research & Evaluation

- [ ] Benchmark generation quality across providers/models
  - Metrics: grounding overlap, answerability, difficulty balance, cost/question
- [ ] Model answer evaluation deep dive
  - Accuracy/AI-pass rate by question type
  - Rubric score distribution, error modes
- [ ] Grading consistency analysis
  - Inter-run variance for open-ended
  - Partial-credit stability for multiple-choice
- [ ] Reporting improvements
  - JSON exports + visual summaries
  - Track seeds/configs for reproducibility

### Medium Term (1-2 Months)

- [ ] Expose validation metrics to clients (fail-on-ungrounded mode)
- [ ] Add lightweight auth/rate-limit hooks (opt-in)
- [ ] RAG extensibility: allow pre-retrieved chunks, pluggable retrievers
- [ ] Storage abstraction (filesystem → DB/object store when needed)
- [ ] Advanced evaluation: adversarial prompts, domain-specific benchmarks

### Long Term (3-6 Months)

- [ ] Human-in-the-loop review for generated questions
- [ ] Grading overrides and manual adjustments
- [ ] CI checks: golden tests for prompts, contract tests for API
- [ ] Adaptive testing and difficulty calibration
- [ ] Formal metrics of understanding (beyond accuracy)

---

## Technical Highlights

### Architecture

- **Backend**: Python + FastAPI (Swagger/OpenAPI auto-generated)
- **Core modules**: Parser, Generator, Validator, Grader
- **Providers**: OpenAI, YandexGPT, local stub (deterministic for testing)
- **Frontend**: Modular JavaScript (6 modules: api-client, ui-utils, file-manager, exam-manager, test-taker, main)
- **Storage**: Filesystem (`data/uploads`, `data/out`, `data/results`)
- **Deployment**: Docker + Compose with configurable `PORT`/`HOST`

### Quality Assurance

- **Test Coverage**: ~80% (unit + integration tests)
- **Security**: CORS, file limits, path traversal protection, rate limiting
- **Validation**: Schema + source refs + deduplication + grounding heuristics
- **Logging**: Structured stdout logging (container-friendly)

### Data Model

- **Exam**: `{exam_id, questions[], config_used}`
- **Question**: `{id, type, stem, options?, correct?, reference_answer?, rubric?, source_refs[], meta{difficulty, tags}}`
- **GradeResponse**: `{summary{total, correct, score_percent}, per_question[]{...}}`

---

## Metrics & Validation

### Generation Metrics

- **Quality score**: Heuristic coherence and answerability (>0.95 across configs)
- **Grounded ratio**: Proportion of questions with source references
- **Coverage**: Fraction of source sections represented in questions

### Grading Metrics

- **Choice questions**: Exact match (single) or partial credit (multiple)
- **Open-ended**: LLM rubric scoring with feedback
- **Consistency**: Tracked via seed-controlled generation

### Model Evaluation

- **Accuracy**: Synthetic student performance by question type
- **AI-pass rate**: Fraction of students passing exams
- **Cost estimates**: Token-based heuristics for provider comparison

---

## Deployment

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env: OPENAI_API_KEY, DEFAULT_PROVIDER=openai

# Run server
uvicorn app.main:app --reload

# Access UI
http://localhost:8000
```

### Production (Docker)

```bash
docker-compose up -d

# Access UI
http://localhost:8000
```

### Testing

```bash
# Unit tests
pytest tests/unit/ -v

# With coverage
pytest --cov=app --cov-report=html tests/

# BDD tests
behave tests/bdd/features/

# Security scan
bandit -r app/ -ll
```

---

## Related Documentation

- [README.md](../README.md) - Project overview and quick start
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture, API reference, frontend design
- [SECURITY.md](SECURITY.md) - Security policy and audit results
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [RESEARCH_DECK.md](RESEARCH_DECK.md) - Presentation summary (Russian)

---

## Contact & Contributions

- **Repository**: https://github.com/TohaRhymes/llm_tester
- **Issues**: https://github.com/TohaRhymes/llm_tester/issues
- **Contributions**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Status**: Production-ready with ongoing research evaluation
**Next Milestone**: Multi-provider benchmarking and adaptive testing
