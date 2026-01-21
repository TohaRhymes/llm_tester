"""
Provider-agnostic LLM interface and factory.
"""
from __future__ import annotations

import hashlib
from typing import Dict, Any, Optional, Literal, Protocol

from app.config import settings
from app.services.openai_client import OpenAIClient
from app.services.yandex_client import YandexGPTClient


ProviderName = Literal["openai", "yandex", "local"]


class LLMProvider(Protocol):
    """Interface implemented by all LLM providers."""

    def generate_question(
        self,
        content: str,
        question_type: str,
        difficulty: str = "medium",
        language: str = "en",
        prompt_variant: Optional[str] = None
    ) -> Dict[str, Any]:
        ...

    def answer_question(
        self,
        question_stem: str,
        question_type: str,
        options: Optional[list[str]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        ...

    def grade_open_ended(
        self,
        question_stem: str,
        reference_answer: str,
        rubric: list[str],
        student_answer: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        ...


class LocalLLMClient:
    """
    Deterministic stub client used for tests and offline usage.

    Generates simple questions from content without external calls.
    """

    def __init__(self, model: str = "local-stub"):
        self.model = model
        self._counter = 0

    def generate_question(
        self,
        content: str,
        question_type: str,
        difficulty: str = "medium",
        language: str = "en",
        prompt_variant: Optional[str] = None
    ) -> Dict[str, Any]:
        # MD5 used for deterministic seed generation only, not cryptography
        seed = int(hashlib.md5(content.encode(), usedforsecurity=False).hexdigest(), 16) % 1000
        self._counter += 1
        keyword = content.split()[0] if content else "content"
        variant_tag = f"[{prompt_variant}]" if prompt_variant else ""
        stem = f"[{language.upper()}][{difficulty}]{variant_tag} Based on {keyword} {seed}, what is the key fact? #{self._counter}"

        if question_type == "open_ended":
            return {
                "stem": stem + " Explain briefly?",
                "reference_answer": f"The key fact from segment {keyword} {seed}.",
                "rubric": [
                    f"Mentions the key fact about {keyword}",
                    "Relates it to the source text",
                    "States in 1-2 sentences"
                ]
            }

        options = [
            f"{keyword} fact {seed % 4}",
            f"{keyword} fact {(seed + 1) % 5}",
            f"{keyword} fact {(seed + 2) % 6}",
            f"{keyword} fact {(seed + 3) % 7}"
        ]

        correct = [0] if question_type == "single_choice" else [0, 1]

        return {
            "stem": stem + " Choose the correct option?",
            "options": options,
            "correct": correct,
            "rubric": [
                "Chooses correct fact",
                "Avoids unrelated options",
                "Matches source meaning"
            ]
        }

    def answer_question(
        self,
        question_stem: str,
        question_type: str,
        options: Optional[list[str]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        if question_type == "open_ended":
            return {"text_answer": "Stub answer based on local model.", "reasoning": "local-stub"}

        return {"choice": [0] if question_type == "single_choice" else [0, 1], "reasoning": "local-stub"}

    def grade_open_ended(
        self,
        question_stem: str,
        reference_answer: str,
        rubric: list[str],
        student_answer: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        score = 1.0 if reference_answer and reference_answer.lower() in student_answer.lower() else 0.5
        rubric_scores = [1 if reference_answer.lower() in student_answer.lower() else 0 for _ in rubric]
        return {
            "rubric_scores": rubric_scores,
            "score": min(1.0, max(0.0, score)),
            "feedback": "Scored by local stub; configure a real provider for production."
        }


def get_llm_client(
    provider: ProviderName = "openai",
    model_name: Optional[str] = None,
    allow_stub_fallback: bool = True
) -> LLMProvider:
    """
    Return an LLM client for the requested provider.

    Falls back to the local stub if credentials are missing and allow_stub_fallback is True.
    """
    provider = provider or "openai"
    model_name = model_name or ""

    if provider == "openai":
        if not settings.openai_api_key and allow_stub_fallback:
            print("⚠️  OPENAI_API_KEY missing; using local stub provider.")
            return LocalLLMClient()
        return OpenAIClient(model_override=model_name or None)

    if provider == "yandex":
        if (not settings.yandex_cloud_api_key or not settings.yandex_folder_id) and allow_stub_fallback:
            print("⚠️  Yandex credentials missing; using local stub provider.")
            return LocalLLMClient()
        return YandexGPTClient(model_override=model_name or None)

    # Default stub
    return LocalLLMClient(model=model_name or "local-stub")
