# Plan (roadmap + evaluation)

## Short Term
- Surface validation metrics (grounded ratio, coverage) in `/api/generate` response and UI.
- Harden exams listing (filters by language/provider) and add download actions.
- Postman/CLI parity: keep provider/model/local stub options consistent; smoke-test collection.

## Research & Evaluation
- Benchmark generation quality across providers/models on shared corpora; metrics: grounding overlap, answerability, coherence, difficulty balance, cost/question.
- Model answer eval: accuracy/AI-pass by question type, rubric score distribution, error modes.
- Grading consistency: inter-run variance for open-ended (same prompts), partial-credit stability for multiple choice.
- Reporting: JSON exports + simple visual summaries; track seeds/configs for reproducibility.

## Medium Term
- Expose validation metrics to clients; optional stricter mode (fail on ungrounded).
- Add lightweight auth/rate-limit hooks (opt-in) and configurable CORS.
- RAG hook: allow passing pre-retrieved chunks, later plug retriever.
- Storage abstraction to swap filesystem for DB/object store when needed.

## Long Term
- Human-in-the-loop review for generated questions and grading overrides.
- Advanced evaluation: adversarial prompts, robustness to prompt injection, domain-specific benchmarks.
- CI checks: stub-based golden tests for prompts/validators, contract tests for API.
