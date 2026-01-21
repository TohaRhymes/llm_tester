"""
Utilities for preprocessing source materials into markdown.
"""
from __future__ import annotations


def sanitize_filename(name: str) -> str:
    """Return a simple filename-safe string."""
    return "_".join(name.strip().split())


def text_to_markdown(text: str, title: str) -> str:
    """Convert plain text to a minimal markdown document."""
    lines = [line.strip() for line in text.splitlines()]
    paragraphs = []
    buffer = []

    for line in lines:
        if not line:
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
            continue
        buffer.append(line)

    if buffer:
        paragraphs.append(" ".join(buffer))

    body = "\n\n".join(paragraphs).strip()
    if not body:
        body = "_No content extracted._"

    return f"# {title}\n\n{body}\n"
