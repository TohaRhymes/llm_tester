# Project Summary (Architecture, Design, Research)

- Architecture: FastAPI service for exam generation/grading; provider-agnostic LLM layer (OpenAI/Yandex/local stub); validation pipeline (schema, source refs, dedup, grounding); exam import/export; Docker/Compose for reproducible runs.
- Core flows: parse markdown → generate questions (counts/ratios, difficulty, language, provider/model) → validate → persist exam; grade answers (local for choice, LLM for open-ended); import existing exams; list/download artifacts.
- Design/UI: web client with gov-inspired palette, provider/model selectors, count-based controls, in-app exam import, and basic exam viewer/test-taker.
- Research tooling: evaluation scripts for generation/model answer benchmarking, grounding/coverage metrics in validation, stub provider for deterministic offline tests; support for multi-model comparisons and grading consistency checks planned.
