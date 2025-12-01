Feature: LLM Evaluation Framework
  As a researcher
  I want to compare different LLM models for question generation and grading
  So that I can select the best model for educational content

  Background:
    Given I have sample medical content
    And I have configured evaluation metrics

  Scenario: Evaluate question generation quality
    When I generate questions using model "gpt-4o-mini"
    And I generate questions using model "gpt-4o"
    Then I should receive quality scores for both models
    And the scores should include answerability metrics
    And the scores should include difficulty distribution metrics
    And the scores should include coherence metrics

  Scenario: Evaluate grading consistency
    Given I have a reference exam with open-ended questions
    And I have sample student answers
    When I grade answers using model "gpt-4o-mini"
    And I grade answers using model "gpt-4o"
    Then I should receive consistency scores
    And the scores should include inter-rater reliability
    And the scores should include score distribution analysis

  Scenario: Compare models side-by-side
    When I run comparative evaluation with models "gpt-4o-mini,gpt-4o"
    Then I should receive a comparison report
    And the report should include generation quality metrics
    And the report should include grading accuracy metrics
    And the report should include cost-performance analysis

  Scenario: Generate evaluation report
    Given I have evaluation results for multiple models
    When I request an evaluation report
    Then I should receive a formatted report with visualizations
    And the report should include model rankings
    And the report should include recommendations

  Scenario: Evaluate with custom metrics
    Given I have defined custom evaluation metrics
    When I run evaluation with custom metrics
    Then the results should include custom metric scores
    And the results should be comparable across models
