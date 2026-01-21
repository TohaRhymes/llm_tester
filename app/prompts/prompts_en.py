"""
English prompts for question generation and grading.
"""

SYSTEM_MESSAGE_EN = "You are an expert educator creating educational test questions. Generate questions in English."

CHOICE_QUESTION_PROMPT_EN = """Based on the following educational content, generate a {difficulty} difficulty test question IN ENGLISH.

Content:
{content}

Requirements:
- {type_instruction}
- Provide 4-5 answer options
- Options must be plausible but clearly distinguishable
- Question must be answerable from the given content
- Use clear, unambiguous language
- Generate a grading rubric with 3-4 specific criteria for evaluating answers

IMPORTANT: Generate EVERYTHING in English, even if the source content is in another language.

Return ONLY a JSON object with this exact structure:
{{
  "stem": "The question text here IN ENGLISH?",
  "options": ["Option A in English", "Option B in English", "Option C", "Option D"],
  "correct": [index_or_indices],
  "rubric": [
    "Criterion 1 (e.g., 'Identifies the correct definition')",
    "Criterion 2 (e.g., 'Explains the key mechanism')",
    "Criterion 3 (e.g., 'Applies knowledge to clinical context')"
  ]
}}

Important:
- {correct_format}
- Indices are 0-based (first option is index 0)
- Rubric items must be specific and measurable
- Do NOT include any additional text, explanations, or markdown
- Return ONLY valid JSON
- ALL TEXT MUST BE IN ENGLISH
"""

OPEN_ENDED_PROMPT_EN = """Based on the following educational content, generate a {difficulty} difficulty open-ended question that requires a written text response IN ENGLISH.

Content:
{content}

Requirements:
- Create a question that tests deeper understanding (not just recall)
- Question should require 2-4 sentences to answer properly
- Provide a complete reference answer that demonstrates expected response
- Create 3-5 specific rubric criteria for grading the answer

IMPORTANT: Generate EVERYTHING in English, even if the source content is in another language.

Examples of good open-ended questions:
- "Explain the pathophysiology of [condition] and describe the key diagnostic criteria."
- "Compare and contrast [concept A] and [concept B], providing clinical examples."
- "Describe the clinical approach to managing [scenario] and justify your reasoning."

Return ONLY a JSON object with this exact structure:
{{
  "stem": "The open-ended question here IN ENGLISH?",
  "reference_answer": "A complete answer IN ENGLISH demonstrating what students should write. Include all key points, reasoning, and specific details from the source material.",
  "rubric": [
    "Clear criterion 1 (e.g., 'Mentions endothelial dysfunction in pathophysiology')",
    "Clear criterion 2 (e.g., 'Lists at least 3 diagnostic criteria with specific values')",
    "Clear criterion 3 (e.g., 'Explains mechanism linking causes to symptoms')"
  ]
}}

Important:
- Reference answer should be 2-4 sentences and comprehensive
- Each rubric item must be specific and measurable
- Rubric should cover all major points in the reference answer
- Do NOT include any additional text, explanations, or markdown
- Return ONLY valid JSON
- ALL TEXT MUST BE IN ENGLISH
"""

GRADING_SYSTEM_EN = "You are an expert educator grading student answers."

# Prompt variants for research comparisons.
CHOICE_PROMPT_VARIANTS_EN = {
    "default": CHOICE_QUESTION_PROMPT_EN,
    "grounded": """Based on the following educational content, generate a {difficulty} difficulty test question IN ENGLISH.

Content:
{content}

Requirements:
- {type_instruction}
- Provide 4-5 answer options
- Each option must be explicitly supported by the content
- Question must be answerable ONLY from the given content
- Use clear, unambiguous language
- Generate a grading rubric with 3-4 specific criteria for evaluating answers

IMPORTANT: Generate EVERYTHING in English, even if the source content is in another language.

Return ONLY a JSON object with this exact structure:
{{
  "stem": "The question text here IN ENGLISH?",
  "options": ["Option A in English", "Option B in English", "Option C", "Option D"],
  "correct": [index_or_indices],
  "rubric": [
    "Criterion 1 (e.g., 'Identifies the correct definition')",
    "Criterion 2 (e.g., 'Explains the key mechanism')",
    "Criterion 3 (e.g., 'Applies knowledge to clinical context')"
  ]
}}

Important:
- {correct_format}
- Indices are 0-based (first option is index 0)
- Rubric items must be specific and measurable
- Do NOT include any additional text, explanations, or markdown
- Return ONLY valid JSON
- ALL TEXT MUST BE IN ENGLISH
""",
    "concise": """Based on the following educational content, generate a {difficulty} difficulty test question IN ENGLISH.

Content:
{content}

Requirements:
- {type_instruction}
- Provide 4-5 answer options
- Keep the stem under 20 words
- Use clear, unambiguous language
- Generate a grading rubric with 3-4 specific criteria for evaluating answers

IMPORTANT: Generate EVERYTHING in English, even if the source content is in another language.

Return ONLY a JSON object with this exact structure:
{{
  "stem": "The question text here IN ENGLISH?",
  "options": ["Option A in English", "Option B in English", "Option C", "Option D"],
  "correct": [index_or_indices],
  "rubric": [
    "Criterion 1 (e.g., 'Identifies the correct definition')",
    "Criterion 2 (e.g., 'Explains the key mechanism')",
    "Criterion 3 (e.g., 'Applies knowledge to clinical context')"
  ]
}}

Important:
- {correct_format}
- Indices are 0-based (first option is index 0)
- Rubric items must be specific and measurable
- Do NOT include any additional text, explanations, or markdown
- Return ONLY valid JSON
- ALL TEXT MUST BE IN ENGLISH
""",
}

OPEN_ENDED_PROMPT_VARIANTS_EN = {
    "default": OPEN_ENDED_PROMPT_EN,
    "grounded": """Based on the following educational content, generate a {difficulty} difficulty open-ended question that requires a written text response IN ENGLISH.

Content:
{content}

Requirements:
- Create a question that tests deeper understanding (not just recall)
- Ensure the answer can be grounded entirely in the provided content
- Provide a complete reference answer that demonstrates expected response
- Create 3-5 specific rubric criteria for grading the answer

IMPORTANT: Generate EVERYTHING in English, even if the source content is in another language.

Return ONLY a JSON object with this exact structure:
{{
  "stem": "The open-ended question here IN ENGLISH?",
  "reference_answer": "A complete answer IN ENGLISH demonstrating what students should write. Include all key points, reasoning, and specific details from the source material.",
  "rubric": [
    "Clear criterion 1 (e.g., 'Mentions endothelial dysfunction in pathophysiology')",
    "Clear criterion 2 (e.g., 'Lists at least 3 diagnostic criteria with specific values')",
    "Clear criterion 3 (e.g., 'Explains mechanism linking causes to symptoms')"
  ]
}}

Important:
- Reference answer should be 2-4 sentences and comprehensive
- Each rubric item must be specific and measurable
- Rubric should cover all major points in the reference answer
- Do NOT include any additional text, explanations, or markdown
- Return ONLY valid JSON
- ALL TEXT MUST BE IN ENGLISH
""",
    "concise": """Based on the following educational content, generate a {difficulty} difficulty open-ended question that requires a written text response IN ENGLISH.

Content:
{content}

Requirements:
- Create a question that tests deeper understanding (not just recall)
- Keep the question under 20 words
- Provide a concise reference answer (2-3 sentences)
- Create 3-5 specific rubric criteria for grading the answer

IMPORTANT: Generate EVERYTHING in English, even if the source content is in another language.

Return ONLY a JSON object with this exact structure:
{{
  "stem": "The open-ended question here IN ENGLISH?",
  "reference_answer": "A complete answer IN ENGLISH demonstrating what students should write. Include all key points, reasoning, and specific details from the source material.",
  "rubric": [
    "Clear criterion 1 (e.g., 'Mentions endothelial dysfunction in pathophysiology')",
    "Clear criterion 2 (e.g., 'Lists at least 3 diagnostic criteria with specific values')",
    "Clear criterion 3 (e.g., 'Explains mechanism linking causes to symptoms')"
  ]
}}

Important:
- Reference answer should be 2-3 sentences and comprehensive
- Each rubric item must be specific and measurable
- Rubric should cover all major points in the reference answer
- Do NOT include any additional text, explanations, or markdown
- Return ONLY valid JSON
- ALL TEXT MUST BE IN ENGLISH
""",
}


def get_choice_prompt_en(variant: str) -> str:
    return CHOICE_PROMPT_VARIANTS_EN.get(variant, CHOICE_PROMPT_VARIANTS_EN["default"])


def get_open_ended_prompt_en(variant: str) -> str:
    return OPEN_ENDED_PROMPT_VARIANTS_EN.get(variant, OPEN_ENDED_PROMPT_VARIANTS_EN["default"])
