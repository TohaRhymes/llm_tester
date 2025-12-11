# Solution Snapshot

## Capabilities
- **Generation**: counts/ratios, difficulty, language (en/ru), provider/model selection; local stub for offline; deterministic with seed.
- **Validation**: schema + source refs + dedup + grounding heuristics (soft by default, logged).
- **Grading**: choice scored locally with partial credit; open-ended via LLM rubric; results persisted.
- **Exams API**: upload/list files, generate, grade, import exams; listing with sorting/pagination.
- **UI**: provider/model selectors, count controls, exam table with pagination, in-app exam import, gov-style palette.
- **Ops**: Docker + Compose (`PORT`/`HOST`), data volume, stdout logs.

## Metrics & Evaluation (current/practical)
- Generation: grounding overlap ratio, section coverage, answerability (implicit), coherence heuristics.
- Grading: partial credit distribution, open-ended rubric scores.
- Model eval scripts (CLI): accuracy/AI pass rate per model, cost estimates (token-based heuristic), grading consistency.

## Operational Notes
- Default provider can be set to `local` for demo; set OpenAI/Yandex keys in `.env` to use real models.
- Exams and grades stored under `data/out/`; uploads under `data/uploads/`; results under `data/results/`.
- Errors: validation issues are soft (logged); unexpected failures return generic 500.
