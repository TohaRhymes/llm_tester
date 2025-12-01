# LLM Evaluation Framework

Comprehensive framework for evaluating and comparing different LLM models for question generation and grading quality.

## Overview

The evaluation framework allows you to:
- **Compare Models**: Test multiple LLMs (gpt-4o-mini, gpt-4o, etc.) side-by-side
- **Measure Quality**: Evaluate question answerability, coherence, and difficulty balance
- **Test Consistency**: Assess grading reliability across multiple runs
- **Analyze Cost**: Calculate cost-performance ratios for model selection

## Quick Start

### Run Evaluation

```bash
# Evaluate default models (gpt-4o-mini, gpt-4o)
python scripts/evaluate_models.py --content examples/medical_content.md

# Evaluate specific models
python scripts/evaluate_models.py --models gpt-4o-mini,gpt-4 --num-questions 20

# Custom output directory
python scripts/evaluate_models.py --output-dir my_evaluations
```

### Example Output

```
Starting evaluation of 2 models...
Content: examples/medical_content.md
Questions per model: 10

Evaluating gpt-4o-mini...
  Quality Score: 0.7850
  Consistency Score: 0.9200
  Avg Generation Time: 2.34s

Evaluating gpt-4o...
  Quality Score: 0.9100
  Consistency Score: 0.9500
  Avg Generation Time: 4.21s

Comparing models...

Evaluation complete!
Results saved to: out/evaluations/evaluation_20241201_120000.json

Recommended model: gpt-4o-mini
Reasoning: gpt-4o has highest quality, but gpt-4o-mini offers better value for cost
```

## Evaluation Metrics

### 1. Question Quality Metrics

**Answerability** (0.0 - 1.0)
- Measures if questions can be answered from source material
- Checks structural validity (options, correct answers, rubrics)
- Higher score = more answerable questions

**Coherence** (0.0 - 1.0)
- Evaluates question stem clarity and structure
- Checks appropriate length and formatting
- Higher score = more coherent questions

**Difficulty Balance** (0.0 - 1.0)
- Analyzes distribution across easy/medium/hard
- Ideal distribution: ~33% each difficulty level
- Higher score = better balance

**Overall Quality** (0.0 - 1.0)
- Weighted average of above metrics
- Formula: `0.4 * answerability + 0.3 * coherence + 0.3 * balance`

### 2. Grading Consistency Metrics

**Inter-Rater Reliability** (0.0 - 1.0)
- Compares scores from two independent grading runs
- Measures consistency of AI grading
- Higher score = more reliable grading

**Score Distribution**
- Mean, standard deviation, min, max of scores
- Helps identify grading patterns

### 3. Model Comparison Metrics

**Cost-Performance Ratio**
- Quality Score / Cost per Question
- Higher ratio = better value

**Rankings**
- Best Overall: Highest quality score
- Best Value: Highest cost-performance ratio

## Evaluation Report Structure

```json
{
  "summary": {
    "models_evaluated": ["gpt-4o-mini", "gpt-4o"],
    "best_model": "gpt-4o",
    "total_questions": 20
  },
  "model_details": {
    "gpt-4o-mini": {
      "quality_score": 0.7850,
      "quality_details": {
        "answerability": 0.9000,
        "coherence": 0.8500,
        "balance_score": 0.6500,
        "difficulty_distribution": {
          "easy": 3,
          "medium": 4,
          "hard": 3
        }
      },
      "consistency_score": 0.9200,
      "avg_generation_time": 2.34,
      "cost_per_question": 0.000075
    },
    "gpt-4o": {
      "quality_score": 0.9100,
      "quality_details": {...},
      "consistency_score": 0.9500,
      "avg_generation_time": 4.21,
      "cost_per_question": 0.001250
    }
  },
  "comparison": {
    "rankings": {
      "quality": ["gpt-4o", "gpt-4o-mini"]
    },
    "best_overall": "gpt-4o",
    "best_value": "gpt-4o-mini",
    "value_scores": {
      "gpt-4o-mini": 10466.67,
      "gpt-4o": 728.00
    }
  },
  "recommendations": {
    "recommended_model": "gpt-4o-mini",
    "alternative": "gpt-4o",
    "reasoning": "gpt-4o has highest quality, but gpt-4o-mini offers better value for cost"
  },
  "timestamp": "2024-12-01T12:00:00.000000"
}
```

## Programmatic Usage

### Using Evaluators Directly

```python
from app.core.evaluator import QuestionQualityEvaluator, GradingConsistencyEvaluator
from app.models.schemas import Question

# Evaluate question quality
evaluator = QuestionQualityEvaluator()
questions = [...]  # List of Question objects
quality = evaluator.evaluate_overall_quality(questions)

print(f"Answerability: {quality['answerability']}")
print(f"Coherence: {quality['coherence']}")
print(f"Overall: {quality['overall']}")

# Evaluate grading consistency
consistency_evaluator = GradingConsistencyEvaluator()
results1 = [...]  # First grading run
results2 = [...]  # Second grading run
reliability = consistency_evaluator.calculate_inter_rater_reliability(results1, results2)
print(f"Inter-rater reliability: {reliability}")
```

### Model Comparison

```python
from app.core.evaluator import ModelComparator

comparator = ModelComparator()
model_results = {
    "gpt-4o-mini": {"quality_score": 0.78, "cost_per_question": 0.000075},
    "gpt-4o": {"quality_score": 0.91, "cost_per_question": 0.001250}
}

comparison = comparator.compare_models(model_results)
print(f"Best overall: {comparison['best_overall']}")
print(f"Best value: {comparison['best_value']}")

recommendation = comparator.generate_recommendation(model_results)
print(f"Recommended: {recommendation['recommended_model']}")
print(f"Reason: {recommendation['reasoning']}")
```

## BDD Test Scenarios

The evaluation framework includes comprehensive BDD scenarios in `tests/bdd/features/evaluation.feature`:

- ✅ Evaluate question generation quality
- ✅ Evaluate grading consistency
- ✅ Compare models side-by-side
- ✅ Generate evaluation reports
- ✅ Custom metrics support

Run BDD tests:
```bash
behave tests/bdd/features/evaluation.feature
```

## Cost Estimates

Approximate costs (as of January 2025):

| Model | Cost per 1M Tokens (Input) | Est. Cost per Question |
|-------|----------------------------|------------------------|
| gpt-4o-mini | $0.15 | $0.000075 |
| gpt-4o | $2.50 | $0.001250 |
| gpt-3.5-turbo | $0.50 | $0.000250 |
| gpt-4 | $30.00 | $0.015000 |

*Estimates assume ~500 tokens per question (generation + grading)*

## Best Practices

### Model Selection

- **High Volume, Cost-Sensitive**: Use `gpt-4o-mini`
  - Good quality at low cost
  - Suitable for production with large question banks

- **Maximum Quality**: Use `gpt-4o`
  - Best generation and grading quality
  - For critical assessments or high-stakes exams

- **Development/Testing**: Use `gpt-4o-mini`
  - Fast iteration cycles
  - Lower costs during development

### Evaluation Frequency

- **Initial Setup**: Evaluate all candidate models
- **Model Updates**: Re-evaluate when OpenAI releases new models
- **Quality Assurance**: Periodic checks (monthly/quarterly)
- **After Prompt Changes**: Re-evaluate if you modify prompts

### Interpreting Results

- **Quality Score > 0.80**: Excellent
- **Quality Score 0.70-0.80**: Good
- **Quality Score < 0.70**: Review and tune prompts

- **Consistency Score > 0.90**: Very reliable
- **Consistency Score 0.80-0.90**: Acceptable
- **Consistency Score < 0.80**: Consider different model or temperature

## Extending the Framework

### Adding Custom Metrics

```python
from app.core.evaluator import QuestionQualityEvaluator

class CustomQualityEvaluator(QuestionQualityEvaluator):
    def evaluate_clinical_relevance(self, questions):
        """Custom metric for clinical relevance."""
        # Your evaluation logic here
        return relevance_score

    def evaluate_overall_quality(self, questions):
        base_quality = super().evaluate_overall_quality(questions)
        base_quality["clinical_relevance"] = self.evaluate_clinical_relevance(questions)
        return base_quality
```

### Adding New Models

Simply update the `--models` parameter:

```bash
python scripts/evaluate_models.py --models gpt-4o-mini,gpt-4o,claude-3-sonnet
```

Note: For non-OpenAI models, you'll need to implement a corresponding client in `app/services/`.

## Troubleshooting

**Issue**: "ModuleNotFoundError: app.core.evaluator"
- **Solution**: Run from project root: `python scripts/evaluate_models.py`

**Issue**: Evaluation takes too long
- **Solution**: Reduce `--num-questions` or evaluate fewer models

**Issue**: Inconsistent results between runs
- **Solution**: Increase sample size (`--num-questions`) for more stable estimates

**Issue**: Cost concerns
- **Solution**: Start with `gpt-4o-mini` only, use small `--num-questions` for testing

## Related Documentation

- [README.md](../README.md) - Project overview
- [PRESENTATION.md](PRESENTATION.md) - Exam defense presentation
- [AUTOMATED_REVIEW.md](AUTOMATED_REVIEW.md) - Verification checklist

## Support

For issues or questions about the evaluation framework:
- GitHub Issues: https://github.com/TohaRhymes/llm_tester/issues
- Tag with `enhancement` or `evaluation` label
