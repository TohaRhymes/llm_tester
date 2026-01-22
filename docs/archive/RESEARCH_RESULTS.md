# Research Results

## Context

During the biobanking school at the Ott Institute, we used lecture materials from instructors to generate tests. The generated items were mixed with standard tests, and the experience was positive.

## Experimental Setup

- Domains: medical (21 markdown files), ML (68 markdown files)
- Question mix: 2 single choice, 2 multiple choice, 2 open-ended
- Prompt variants: default, grounded
- RAG settings: off/on (top_k=3)
- Students: 48 synthetic profiles
- Provider: local stub (deterministic)

## Summary Metrics (Medical)

| Variant  | RAG | Quality | Grounded | Coverage | Mean Score | Open-Ended | Choice |
|----------|-----|---------|----------|----------|------------|------------|--------|
| default  | off | 0.9540  | 0.2380   | 1.0000   | 52.60      | 0.5000     | 0.5389 |
| grounded | off | 0.9683  | 0.2380   | 1.0000   | 52.35      | 0.5000     | 0.5352 |
| default  | on  | 0.9667  | 0.2539   | 1.0000   | 52.02      | 0.5000     | 0.5303 |
| grounded | on  | 0.9540  | 0.2619   | 1.0000   | 52.58      | 0.5000     | 0.5387 |

## Summary Metrics (ML)

| Variant  | RAG | Quality | Grounded | Coverage | Mean Score | Open-Ended | Choice |
|----------|-----|---------|----------|----------|------------|------------|--------|
| default  | off | 0.9608  | 0.7598   | 0.4999   | 51.98      | 0.5000     | 0.5296 |
| grounded | off | 0.9579  | 0.7818   | 0.5080   | 52.38      | 0.5000     | 0.5358 |
| default  | on  | 0.9529  | 0.7426   | 0.3556   | 52.74      | 0.5000     | 0.5411 |
| grounded | on  | 0.9544  | 0.7843   | 0.3528   | 52.54      | 0.5000     | 0.5381 |

## RAGAS (Subsampled, 5 docs per domain, max 20 open-ended samples per config)

Medical:
- default|rag=off: faithfulness=nan, answer_relevancy=0.0787, context_precision=0.0, context_recall=0.0
- grounded|rag=off: faithfulness=nan, answer_relevancy=0.0, context_precision=0.0, context_recall=0.0
- default|rag=on: faithfulness=nan, answer_relevancy=0.0, context_precision=0.0, context_recall=0.0
- grounded|rag=on: faithfulness=nan, answer_relevancy=0.0814, context_precision=0.0, context_recall=0.0

ML:
- default|rag=off: faithfulness=nan, answer_relevancy=0.0, context_precision=0.0, context_recall=0.2
- grounded|rag=off: faithfulness=nan, answer_relevancy=0.0, context_precision=0.1, context_recall=0.1
- default|rag=on: faithfulness=nan, answer_relevancy=0.0754, context_precision=0.0, context_recall=0.1
- grounded|rag=on: faithfulness=nan, answer_relevancy=0.0, context_precision=0.1, context_recall=0.2

Notes:
- Some medical markdown files only contain a top-level heading, which reduces grounding ratio in the validator.
- RAGAS faithfulness is NaN because synthetic open-ended answers are short and often do not yield extractable statements.
