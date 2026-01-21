"""
OpenAI API client wrapper for question generation.
"""
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from app.config import settings
from app.prompts import prompts_en, prompts_ru


class OpenAIClient:
    """Wrapper for OpenAI API calls."""

    def __init__(self, model_override: Optional[str] = None):
        """Initialize OpenAI client with API key from settings."""
        self.model = model_override or settings.openai_model
        self.client = None

        if settings.openai_api_key:
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )

    def generate_question(
        self,
        content: str,
        question_type: str,
        difficulty: str = "medium",
        language: str = "en",
        prompt_variant: str = "default"
    ) -> Dict[str, Any]:
        """
        Generate a single question from content.

        Args:
            content: Source content to generate question from
            question_type: "single_choice", "multiple_choice", or "open_ended"
            difficulty: "easy", "medium", or "hard"
            language: "en" for English or "ru" for Russian

        Returns:
            Dict with question data (stem, options, correct, rubric) for all types
        """
        prompt = self._build_prompt(content, question_type, difficulty, language, prompt_variant)

        # Get language-specific system message
        prompts_module = prompts_ru if language == "ru" else prompts_en
        system_message = prompts_module.SYSTEM_MESSAGE_RU if language == "ru" else prompts_module.SYSTEM_MESSAGE_EN

        try:
            if not self.client:
                raise RuntimeError("OpenAI client not configured. Set OPENAI_API_KEY or use provider='local'.")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_message
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
                if not all(k in result for k in ["stem", "options", "correct", "rubric"]):
                    raise ValueError("Invalid response from OpenAI: missing required fields for choice questions")

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to generate question: {str(e)}")

    def _build_prompt(
        self,
        content: str,
        question_type: str,
        difficulty: str,
        language: str,
        prompt_variant: str
    ) -> str:
        """
        Build prompt for question generation.

        Args:
            content: Source content
            question_type: Type of question
            difficulty: Difficulty level
            language: "en" or "ru"

        Returns:
            Formatted prompt string
        """
        if question_type == "open_ended":
            from app.prompts.registry import get_prompt_template
            template = get_prompt_template(language, question_type, prompt_variant)
            return template.format(content=content, difficulty=difficulty)

        # Choice questions (single or multiple)
        if question_type == "single_choice":
            if language == "ru":
                type_instruction = "Создайте вопрос с ОДНИМ правильным ответом."
                correct_format = "Поле 'correct' должно содержать список с ОДНИМ индексом (например, [2])."
            else:
                type_instruction = "Create a single-choice question with EXACTLY ONE correct answer."
                correct_format = "The 'correct' field must be a list with exactly ONE index (e.g., [2])."
        else:
            if language == "ru":
                type_instruction = "Создайте вопрос с множественным выбором с 2-3 правильными ответами."
                correct_format = "Поле 'correct' должно содержать список с 2-3 индексами (например, [1, 3])."
            else:
                type_instruction = "Create a multiple-choice question with 2-3 correct answers."
                correct_format = "The 'correct' field must be a list with 2-3 indices (e.g., [1, 3])."

        from app.prompts.registry import get_prompt_template
        template = get_prompt_template(language, question_type, prompt_variant)
        return template.format(
            content=content,
            difficulty=difficulty,
            type_instruction=type_instruction,
            correct_format=correct_format
        )

    def answer_question(
        self,
        question_stem: str,
        question_type: str,
        options: list[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Answer a question using OpenAI.

        Args:
            question_stem: The question text
            question_type: "single_choice", "multiple_choice", or "open_ended"
            options: List of answer options (for choice questions)
            language: "en" or "ru"

        Returns:
            Dict with answer data (choice indices for MCQ, text_answer for open-ended)
        """
        if question_type == "open_ended":
            prompt = f"Answer the following question in detail:\n\n{question_stem}"
        else:
            options_text = "\n".join([f"{i}. {opt}" for i, opt in enumerate(options)])
            if question_type == "single_choice":
                prompt = f"Question: {question_stem}\n\nOptions:\n{options_text}\n\nSelect the ONE correct answer. Respond with ONLY the option number (0, 1, 2, etc.)."
            else:
                prompt = f"Question: {question_stem}\n\nOptions:\n{options_text}\n\nSelect ALL correct answers. Respond with the option numbers separated by commas."

        try:
            if not self.client:
                raise RuntimeError("OpenAI client not configured. Set OPENAI_API_KEY or use provider='local'.")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant answering exam questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            answer_text = response.choices[0].message.content.strip()

            if question_type == "open_ended":
                return {
                    "text_answer": answer_text,
                    "reasoning": "Generated by OpenAI"
                }
            else:
                # Parse choice indices
                import re
                numbers = re.findall(r'\b(\d+)\b', answer_text)
                indices = [int(n) for n in numbers if 0 <= int(n) < len(options)]
                if not indices:
                    indices = [0]  # Default to first option

                return {
                    "choice": indices,
                    "reasoning": answer_text
                }

        except Exception as e:
            raise RuntimeError(f"Failed to answer question: {str(e)}")

    def grade_open_ended(
        self,
        question_stem: str,
        reference_answer: str,
        rubric: list[str],
        student_answer: str,
        language: str = "en"
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
            if not self.client:
                raise RuntimeError("OpenAI client not configured. Set OPENAI_API_KEY or use provider='local'.")

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
