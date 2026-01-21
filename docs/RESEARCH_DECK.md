# LLM Test Generator — Semester Report

---

## Motivation

- Build a working LLM-based test generator
- Check whether tests measure knowledge or guessing
- Expose limitations of classical testing formats
- Set a base for future research

---

## Goals

- Working prototype (generation + grading)
- Evaluation of quality and grounding
- Experiments with AI strategies and robustness
- Real-world trial with educational materials

---

## System Overview

- Markdown/PDF ingestion
- Question generation (SC/MC/Open-ended)
- Validator (grounding + coverage)
- Auto-grading with rubrics
- Research runner for metrics

---

## Data & Domains

- Medical: 21 lecture files
- ML: 68 lecture files
- Mixed difficulty, RU/EN support
- Synthetic students: 48 profiles for evaluation

---

## Experiment Design

- Prompt variants: default vs grounded
- RAG on/off (top_k=3)
- Metrics: quality, grounding, coverage
- Grading: mean score, open-ended mean
- RAGAS (subsample) for answer metrics

---

## Key Results

- ML: grounded prompts improve grounded_ratio
- RAG reduces coverage but keeps quality stable
- Open-ended grading needs richer responses for RAGAS
- Classic tests are easy for LLMs without understanding

---

## Real-World Pilot

- Biobanking school at Ott Institute
- Used lecture materials + generated tests
- Tests mixed with standard ones
- Experience positive and usable in practice

---

## Main Insight

Classic test formats are vulnerable to LLMs; passing does not imply understanding.
We need deeper evaluation and better metrics for knowledge measurement.

---

## Next Steps (Research)

- Adaptive testing and difficulty calibration
- Formal metrics of understanding
- Stronger experimental design
- Focus on boundaries of knowledge, not only generation

---

## Deliverables

- Working prototype (generation + grading)
- Research evaluation pipeline
- Prompt comparison tooling
- PDF and Markdown ingestion
- Results tables in `docs/RESEARCH_RESULTS.md`
