"""
OpenAI API client wrapper for question generation.
"""
import json
from typing import Dict, Any
from openai import OpenAI
from app.config import settings


class OpenAIClient:
    """Wrapper for OpenAI API calls."""

    def __init__(self):
        """Initialize OpenAI client with API key from settings."""
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        self.model = settings.openai_model

    def generate_question(
        self,
        content: str,
        question_type: str,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate a single question from content.

        Args:
            content: Source content to generate question from
            question_type: "single_choice", "multiple_choice", or "open_ended"
            difficulty: "easy", "medium", or "hard"

        Returns:
            Dict with question data (stem, options, correct) or (stem, reference_answer, rubric)
        """
        prompt = self._build_prompt(content, question_type, difficulty)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical educator creating educational test questions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # Validate result has required fields based on question type
            if question_type == "open_ended":
                if not all(k in result for k in ["stem", "reference_answer", "rubric"]):
                    raise ValueError("Invalid response from OpenAI: missing required fields for open_ended")
            else:
                if not all(k in result for k in ["stem", "options", "correct"]):
                    raise ValueError("Invalid response from OpenAI: missing required fields for choice questions")

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to generate question: {str(e)}")

    def _build_prompt(self, content: str, question_type: str, difficulty: str) -> str:
        """
        Build prompt for question generation.

        Args:
            content: Source content
            question_type: Type of question
            difficulty: Difficulty level

        Returns:
            Formatted prompt string
        """
        if question_type == "open_ended":
            return self._build_open_ended_prompt(content, difficulty)

        if question_type == "single_choice":
            type_instruction = "Create a single-choice question with EXACTLY ONE correct answer."
            correct_format = "The 'correct' field must be a list with exactly ONE index (e.g., [2])."
        else:
            type_instruction = "Create a multiple-choice question with 2-3 correct answers."
            correct_format = "The 'correct' field must be a list with 2-3 indices (e.g., [1, 3])."

        prompt = f"""Based on the following medical content, generate a {difficulty} difficulty test question.

Content:
{content}

Requirements:
- {type_instruction}
- Provide 4-5 answer options
- Options must be plausible but clearly distinguishable
- Question must be answerable from the given content
- Use clear, unambiguous language

Return ONLY a JSON object with this exact structure:
{{
  "stem": "The question text here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct": [index_or_indices]
}}

Important:
- {correct_format}
- Indices are 0-based (first option is index 0)
- Do NOT include any additional text, explanations, or markdown
- Return ONLY valid JSON
"""
        return prompt

    def _build_open_ended_prompt(self, content: str, difficulty: str) -> str:
        """
        Build prompt for open-ended question generation.

        Args:
            content: Source content
            difficulty: Difficulty level

        Returns:
            Formatted prompt string
        """
        prompt = f"""Based on the following medical content, generate a {difficulty} difficulty open-ended question that requires a written text response.

Content:
{content}

Requirements:
- Create a question that tests deeper understanding (not just recall)
- Question should require 2-4 sentences to answer properly
- Provide a complete reference answer that demonstrates expected response
- Create 3-5 specific rubric criteria for grading the answer

Examples of good open-ended questions:
- "Explain the pathophysiology of [condition] and describe the key diagnostic criteria."
- "Compare and contrast [concept A] and [concept B], providing clinical examples."
- "Describe the clinical approach to managing [scenario] and justify your reasoning."

Return ONLY a JSON object with this exact structure:
{{
  "stem": "The open-ended question here?",
  "reference_answer": "A complete answer demonstrating what students should write. Include all key points, clinical reasoning, and specific details from the source material.",
  "rubric": [
    "Clear criterion 1 (e.g., 'Mentions endothelial dysfunction in pathophysiology')",
    "Clear criterion 2 (e.g., 'Lists at least 3 diagnostic criteria with specific values')",
    "Clear criterion 3 (e.g., 'Explains mechanism linking placental ischemia to symptoms')"
  ]
}}

Important:
- Reference answer should be 2-4 sentences and comprehensive
- Each rubric item must be specific and measurable
- Rubric should cover all major points in the reference answer
- Do NOT include any additional text, explanations, or markdown
- Return ONLY valid JSON
"""
        return prompt

    def grade_open_ended(
        self,
        question_stem: str,
        reference_answer: str,
        rubric: list[str],
        student_answer: str
    ) -> Dict[str, Any]:
        """
        Grade an open-ended answer using AI.

        Args:
            question_stem: The question text
            reference_answer: Model answer
            rubric: List of grading criteria
            student_answer: Student's text response

        Returns:
            Dict with score (0.0-1.0), rubric_scores, and feedback
        """
        prompt = f"""You are an expert medical educator grading a student's answer to an open-ended question.

Question:
{question_stem}

Reference Answer:
{reference_answer}

Grading Rubric:
{chr(10).join(f'{i+1}. {criterion}' for i, criterion in enumerate(rubric))}

Student's Answer:
{student_answer}

Task:
1. Evaluate the student's answer against EACH rubric criterion
2. Assign 0 (not met) or 1 (met) to each criterion
3. Calculate overall score as: (met criteria) / (total criteria)
4. Provide constructive feedback highlighting what was good and what was missing

Return ONLY a JSON object with this exact structure:
{{
  "rubric_scores": [0 or 1 for each criterion],
  "score": 0.0-1.0,
  "feedback": "Constructive feedback for the student (2-3 sentences)"
}}

Important:
- Be fair but rigorous - partial matches count only if substantially correct
- Feedback should be specific and actionable
- Score must equal (sum of rubric_scores) / (number of criteria)
- Return ONLY valid JSON
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical educator grading student responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent grading
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # Validate result
            if not all(k in result for k in ["rubric_scores", "score", "feedback"]):
                raise ValueError("Invalid grading response: missing required fields")

            if len(result["rubric_scores"]) != len(rubric):
                raise ValueError(f"Rubric scores count mismatch: expected {len(rubric)}, got {len(result['rubric_scores'])}")

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to grade open-ended answer: {str(e)}")
