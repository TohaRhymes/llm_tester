"""
Markdown parser for extracting structured content from educational materials.
"""
from dataclasses import dataclass
from typing import List, Optional
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode


@dataclass
class ParsedSection:
    """Represents a parsed section from Markdown document."""
    heading: str
    content: str
    level: int
    start_pos: int
    end_pos: int

    def __post_init__(self):
        """Validate section positions."""
        if self.end_pos < self.start_pos:
            raise ValueError(f"end_pos ({self.end_pos}) must be >= start_pos ({self.start_pos})")
        if self.start_pos < 0:
            raise ValueError(f"start_pos ({self.start_pos}) must be >= 0")


@dataclass
class ParsedDocument:
    """Represents a parsed Markdown document."""
    title: Optional[str]
    sections: List[ParsedSection]
    source_text: str

    def get_section(self, heading: str) -> Optional[ParsedSection]:
        """Get section by heading name."""
        for section in self.sections:
            if section.heading == heading:
                return section
        return None


class MarkdownParser:
    """Parser for Markdown educational content."""

    def __init__(self):
        """Initialize parser with markdown-it."""
        self.md = MarkdownIt()

    def parse(self, markdown_text: str) -> ParsedDocument:
        """
        Parse Markdown text into structured document.

        Args:
            markdown_text: Raw Markdown content

        Returns:
            ParsedDocument with title, sections, and source text
        """
        if not markdown_text or not markdown_text.strip():
            return ParsedDocument(title=None, sections=[], source_text=markdown_text)

        tokens = self.md.parse(markdown_text)

        title = None
        sections = []
        current_section = None
        current_heading = None
        current_level = None
        current_content_tokens = []
        heading_start_pos = 0

        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                # Save previous section if exists
                if current_heading is not None:
                    content = self._tokens_to_text(current_content_tokens, markdown_text)
                    end_pos = token.map[0] if token.map else len(markdown_text)
                    sections.append(ParsedSection(
                        heading=current_heading,
                        content=content.strip(),
                        level=current_level,
                        start_pos=heading_start_pos,
                        end_pos=self._get_char_pos(markdown_text, end_pos)
                    ))
                    current_content_tokens = []

                # Start new section
                current_level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
                heading_start_pos = self._get_char_pos(markdown_text, token.map[0]) if token.map else 0

            elif token.type == "inline" and i > 0 and tokens[i-1].type == "heading_open":
                # This is heading content
                heading_text = token.content

                if current_level == 1 and title is None:
                    title = heading_text
                    current_heading = None  # H1 is title, not a section
                else:
                    current_heading = heading_text

            elif token.type == "heading_close":
                # Heading closed, start collecting content
                pass

            elif current_heading is not None:
                # Collect content tokens for current section
                current_content_tokens.append(token)

        # Save last section
        if current_heading is not None:
            content = self._tokens_to_text(current_content_tokens, markdown_text)
            sections.append(ParsedSection(
                heading=current_heading,
                content=content.strip(),
                level=current_level,
                start_pos=heading_start_pos,
                end_pos=len(markdown_text)
            ))

        return ParsedDocument(
            title=title,
            sections=sections,
            source_text=markdown_text
        )

    def _tokens_to_text(self, tokens: List, source_text: str) -> str:
        """
        Convert tokens to plain text content.

        Args:
            tokens: List of markdown-it tokens
            source_text: Original source text

        Returns:
            Extracted text content
        """
        content_parts = []

        for token in tokens:
            if token.type == "inline":
                content_parts.append(token.content)
            elif token.type == "paragraph_open":
                pass
            elif token.type == "paragraph_close":
                content_parts.append("\n")
            elif token.type == "bullet_list_open":
                pass
            elif token.type == "list_item_open":
                pass
            elif token.type == "list_item_close":
                content_parts.append("\n")

        return "".join(content_parts)

    def _get_char_pos(self, text: str, line_num: int) -> int:
        """
        Convert line number to character position.

        Args:
            text: Source text
            line_num: Line number (0-indexed)

        Returns:
            Character position in text
        """
        lines = text.split('\n')
        pos = 0
        for i in range(min(line_num, len(lines))):
            pos += len(lines[i]) + 1  # +1 for newline
        return pos
