Feature: Generate exam questions from educational content
  As a teacher
  I want to generate test questions from educational materials
  So that I can quickly create exams for my students

  Background:
    Given I have medical educational content in Markdown format

  Scenario: Generate exam with default configuration
    When I request exam generation with default settings
    Then I receive a generated exam
    And the exam contains 20 questions
    And the questions have appropriate mix of single and multiple choice
    And each question has source references

  Scenario: Generate exam with custom question count
    When I request exam generation with 10 questions
    Then I receive a generated exam
    And the exam contains exactly 10 questions

  Scenario: Generate exam with custom type ratios
    When I request exam generation with 80% single choice and 20% multiple choice
    Then I receive a generated exam
    And approximately 80% of questions are single choice
    And approximately 20% of questions are multiple choice

  Scenario: Generate exam saves to file
    When I request exam generation
    Then I receive a generated exam
    And the exam is saved to the output directory
    And the exam file contains all question data

  Scenario: Attempt to generate from empty content
    Given I have empty Markdown content
    When I request exam generation
    Then I receive a validation error
    And the error indicates missing content

  Scenario: Generated questions have valid structure
    When I request exam generation with 5 questions
    Then I receive a generated exam
    And each question has a unique ID
    And each question has a stem (question text)
    And each question has 3-5 options
    And each question has correct answer indices
    And single choice questions have exactly 1 correct answer
    And multiple choice questions have 2 or more correct answers
