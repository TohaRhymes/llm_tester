"""
YandexGPT API client wrapper for question generation and answering.
"""
import json
import re
import requests
from typing import Dict, Any, List, Optional
from app.config import settings
from app.prompts import prompts_en, prompts_ru


class YandexGPTClient:
    """Wrapper for YandexGPT API calls."""

    API_ENDPOINT = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def __init__(self, model_override: Optional[str] = None):
        """Initialize YandexGPT client with credentials from settings."""
        if not settings.yandex_cloud_api_key:
            raise ValueError("YANDEX_CLOUD_API_KEY not set in environment")
        if not settings.yandex_folder_id:
            raise ValueError("YANDEX_FOLDER_ID not set in environment")

        self.api_key = settings.yandex_cloud_api_key
        self.folder_id = settings.yandex_folder_id
        self.model = model_override or settings.yandex_model

    def _make_request(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Make a request to YandexGPT API.

        Args:
            messages: List of message dicts with role and text
            temperature: Sampling temperature

        Returns:
            Response text from the model

        Raises:
            RuntimeError: If API request fails
        """
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}/latest",
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": 2000
            },
            "messages": messages
        }

        try:
            response = requests.post(
                self.API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"YandexGPT API error: {response.status_code} - {response.text}"
                )

            result = response.json()
            return result["result"]["alternatives"][0]["message"]["text"]

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to connect to YandexGPT API: {str(e)}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Invalid response from YandexGPT API: {str(e)}")

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
            prompt_variant: Prompt variant name for research comparisons

        Returns:
            Dict with question data (stem, options, correct, rubric) for all types
        """
        prompt = self._build_generation_prompt(content, question_type, difficulty, language, prompt_variant)

        # Get language-specific system message
        prompts_module = prompts_ru if language == "ru" else prompts_en
        system_message = prompts_module.SYSTEM_MESSAGE_RU if language == "ru" else prompts_module.SYSTEM_MESSAGE_EN

        messages = [
            {"role": "system", "text": system_message},
            {"role": "user", "text": prompt}
        ]

        try:
            response_text = self._make_request(messages, temperature=0.7)

            # Parse JSON from response
            result = self._extract_json(response_text)

            # Validate result has required fields based on question type
            if question_type == "open_ended":
                if not all(k in result for k in ["stem", "reference_answer", "rubric"]):
                    raise ValueError("Invalid response: missing required fields for open_ended")
            else:
                if not all(k in result for k in ["stem", "options", "correct", "rubric"]):
                    raise ValueError("Invalid response: missing required fields for choice questions")

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to generate question: {str(e)}")

    def _build_generation_prompt(
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
        options: Optional[List[str]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Answer a question using YandexGPT.

        Args:
            question_stem: The question text
            question_type: "single_choice", "multiple_choice", or "open_ended"
            options: List of answer options (for choice questions)
            language: "en" or "ru"

        Returns:
            Dict with answer data (choice indices for MCQ, text_answer for open-ended)
        """
        prompt = self._build_answer_prompt(question_stem, question_type, options, language)

        messages = [
            {
                "role": "system",
                "text": "You are a helpful assistant answering exam questions."
            },
            {"role": "user", "text": prompt}
        ]

        try:
            response_text = self._make_request(messages, temperature=0.3)

            if question_type == "open_ended":
                return {
                    "text_answer": response_text.strip(),
                    "reasoning": "Generated by YandexGPT"
                }
            else:
                # Parse choice indices from response
                indices = self._extract_choice_indices(response_text, options)
                return {
                    "choice": indices,
                    "reasoning": response_text
                }

        except Exception as e:
            raise RuntimeError(f"Failed to answer question: {str(e)}")

    def _build_answer_prompt(
        self,
        question_stem: str,
        question_type: str,
        options: Optional[List[str]],
        language: str
    ) -> str:
        """Build prompt for answering a question."""
        if question_type == "open_ended":
            if language == "ru":
                return f"""Ответьте на следующий вопрос подробно и точно:

{question_stem}

Дайте развёрнутый ответ."""
            else:
                return f"""Answer the following question in detail and accurately:

{question_stem}

Provide a comprehensive answer."""

        # Choice questions
        options_text = "\n".join([f"{i}. {opt}" for i, opt in enumerate(options)])

        if question_type == "single_choice":
            if language == "ru":
                return f"""Вопрос: {question_stem}

Варианты ответа:
{options_text}

Выберите ОДИН правильный вариант. Ответьте номером варианта (0, 1, 2, и т.д.)."""
            else:
                return f"""Question: {question_stem}

Options:
{options_text}

Select the ONE correct answer. Respond with the option number (0, 1, 2, etc.)."""
        else:
            if language == "ru":
                return f"""Вопрос: {question_stem}

Варианты ответа:
{options_text}

Выберите ВСЕ правильные варианты. Ответьте номерами вариантов через запятую."""
            else:
                return f"""Question: {question_stem}

Options:
{options_text}

Select ALL correct answers. Respond with the option numbers separated by commas."""

    def _extract_choice_indices(self, response_text: str, options: List[str]) -> List[int]:
        """
        Extract choice indices from model response.

        Args:
            response_text: Model's response
            options: List of available options

        Returns:
            List of selected indices
        """
        # Try to find numbers in the response
        numbers = re.findall(r'\b(\d+)\b', response_text)

        if numbers:
            indices = [int(n) for n in numbers if 0 <= int(n) < len(options)]
            if indices:
                return indices

        # Fallback: check if option text is mentioned
        indices = []
        for i, option in enumerate(options):
            if option.lower() in response_text.lower():
                indices.append(i)

        # Last resort: return first option
        return indices if indices else [0]

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text that may contain markdown or other formatting.

        Args:
            text: Text potentially containing JSON

        Returns:
            Parsed JSON object
        """
        # Try direct JSON parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find any JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not extract valid JSON from response: {text[:200]}")

    def grade_open_ended(
        self,
        question_stem: str,
        reference_answer: str,
        rubric: List[str],
        student_answer: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Grade an open-ended answer using YandexGPT.

        Args:
            question_stem: The question text
            reference_answer: Model answer
            rubric: List of grading criteria
            student_answer: Student's text response
            language: "en" or "ru"

        Returns:
            Dict with score (0.0-1.0), rubric_scores, and feedback
        """
        if language == "ru":
            prompt = f"""Вы — эксперт-преподаватель, оценивающий ответ студента на открытый вопрос.

Вопрос:
{question_stem}

Эталонный ответ:
{reference_answer}

Критерии оценивания:
{chr(10).join(f'{i+1}. {criterion}' for i, criterion in enumerate(rubric))}

Ответ студента:
{student_answer}

Задача:
1. Оцените ответ студента по КАЖДОМУ критерию
2. Поставьте 0 (не выполнено) или 1 (выполнено) каждому критерию
3. Рассчитайте общий балл как: (выполненные критерии) / (всего критериев)
4. Дайте конструктивную обратную связь

Верните ТОЛЬКО JSON объект с такой структурой:
{{
  "rubric_scores": [0 или 1 для каждого критерия],
  "score": 0.0-1.0,
  "feedback": "Конструктивная обратная связь (2-3 предложения)"
}}"""
        else:
            prompt = f"""You are an expert educator grading a student's answer to an open-ended question.

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
4. Provide constructive feedback

Return ONLY a JSON object with this exact structure:
{{
  "rubric_scores": [0 or 1 for each criterion],
  "score": 0.0-1.0,
  "feedback": "Constructive feedback (2-3 sentences)"
}}"""

        messages = [
            {"role": "system", "text": "You are an expert educator grading student responses."},
            {"role": "user", "text": prompt}
        ]

        try:
            response_text = self._make_request(messages, temperature=0.3)
            result = self._extract_json(response_text)

            # Validate result
            if not all(k in result for k in ["rubric_scores", "score", "feedback"]):
                raise ValueError("Invalid grading response: missing required fields")

            if len(result["rubric_scores"]) != len(rubric):
                raise ValueError(
                    f"Rubric scores count mismatch: expected {len(rubric)}, "
                    f"got {len(result['rubric_scores'])}"
                )

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to grade open-ended answer: {str(e)}")
