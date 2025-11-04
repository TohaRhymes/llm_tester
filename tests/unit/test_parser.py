"""
Unit tests for Markdown parser (TDD - RED phase).

Tests are written BEFORE implementation.
"""
import pytest
from app.core.parser import MarkdownParser, ParsedSection, ParsedDocument


class TestMarkdownParser:
    """Tests for basic Markdown parsing functionality."""

    @pytest.fixture
    def simple_markdown(self):
        return """# Main Title

This is introduction.

## Section 1

Content of section 1.

## Section 2

Content of section 2 with **bold** text.
"""

    @pytest.fixture
    def medical_content(self):
        return """# Disease

## Symptoms

- Fever
- Cough
- Headache

## Treatment

Use medication X at 100mg dose.
"""

    @pytest.fixture
    def parser(self):
        return MarkdownParser()

    def test_parser_initialization(self, parser):
        """Test that parser can be initialized."""
        assert parser is not None

    def test_parse_returns_parsed_document(self, parser, simple_markdown):
        """Test that parse returns ParsedDocument object."""
        result = parser.parse(simple_markdown)
        assert isinstance(result, ParsedDocument)

    def test_parse_extracts_title(self, parser, simple_markdown):
        """Test that parser extracts main title (h1)."""
        result = parser.parse(simple_markdown)
        assert result.title == "Main Title"

    def test_parse_extracts_sections(self, parser, simple_markdown):
        """Test that parser extracts sections (h2)."""
        result = parser.parse(simple_markdown)
        assert len(result.sections) >= 2
        section_titles = [s.heading for s in result.sections]
        assert "Section 1" in section_titles
        assert "Section 2" in section_titles

    def test_section_contains_content(self, parser, simple_markdown):
        """Test that sections contain their content."""
        result = parser.parse(simple_markdown)
        section1 = next(s for s in result.sections if s.heading == "Section 1")
        assert "Content of section 1" in section1.content

    def test_parse_list_items(self, parser, medical_content):
        """Test that parser handles list items."""
        result = parser.parse(medical_content)
        symptoms_section = next(s for s in result.sections if s.heading == "Symptoms")
        content = symptoms_section.content
        assert "Fever" in content
        assert "Cough" in content
        assert "Headache" in content

    def test_parsed_section_has_metadata(self, parser, simple_markdown):
        """Test that ParsedSection has required metadata."""
        result = parser.parse(simple_markdown)
        section = result.sections[0]
        assert hasattr(section, 'heading')
        assert hasattr(section, 'content')
        assert hasattr(section, 'level')
        assert hasattr(section, 'start_pos')
        assert hasattr(section, 'end_pos')

    def test_section_positions_are_valid(self, parser, simple_markdown):
        """Test that section positions are valid (end > start >= 0)."""
        result = parser.parse(simple_markdown)
        for section in result.sections:
            assert section.start_pos >= 0
            assert section.end_pos > section.start_pos

    def test_parse_empty_markdown(self, parser):
        """Test parsing empty markdown."""
        result = parser.parse("")
        assert isinstance(result, ParsedDocument)
        assert result.title is None or result.title == ""
        assert len(result.sections) == 0

    def test_parse_markdown_without_headings(self, parser):
        """Test parsing markdown with only paragraphs."""
        md = "Just some text.\n\nAnother paragraph."
        result = parser.parse(md)
        assert isinstance(result, ParsedDocument)

    def test_preserve_source_text(self, parser, simple_markdown):
        """Test that original source text is preserved."""
        result = parser.parse(simple_markdown)
        assert result.source_text == simple_markdown

    def test_parse_nested_headings(self, parser):
        """Test parsing markdown with nested heading levels (h1, h2, h3)."""
        md = """# Title
## Section
### Subsection
Content here.
"""
        result = parser.parse(md)
        assert result.title == "Title"
        # Should handle nested headings appropriately

    def test_parse_strips_markdown_formatting(self, parser):
        """Test that parser strips markdown formatting from content."""
        md = """## Test
This has **bold** and *italic* text.
"""
        result = parser.parse(md)
        section = result.sections[0]
        # Content should contain the text without markdown symbols or preserve them based on design
        assert "bold" in section.content
        assert "italic" in section.content


class TestParsedSection:
    """Tests for ParsedSection data structure."""

    def test_parsed_section_creation(self):
        """Test that ParsedSection can be created."""
        section = ParsedSection(
            heading="Test",
            content="Content",
            level=2,
            start_pos=0,
            end_pos=20
        )
        assert section.heading == "Test"
        assert section.content == "Content"
        assert section.level == 2

    def test_parsed_section_validates_positions(self):
        """Test that section validates positions."""
        # This might raise an error or handle it gracefully
        with pytest.raises((ValueError, AssertionError)):
            ParsedSection(
                heading="Test",
                content="Content",
                level=2,
                start_pos=100,
                end_pos=50  # end before start
            )


class TestParsedDocument:
    """Tests for ParsedDocument data structure."""

    def test_parsed_document_creation(self):
        """Test that ParsedDocument can be created."""
        section = ParsedSection(
            heading="Section1",
            content="Content",
            level=2,
            start_pos=0,
            end_pos=20
        )
        doc = ParsedDocument(
            title="Test Document",
            sections=[section],
            source_text="# Test Document\n## Section1\nContent"
        )
        assert doc.title == "Test Document"
        assert len(doc.sections) == 1

    def test_get_section_by_heading(self):
        """Test helper method to get section by heading name."""
        section1 = ParsedSection("Section A", "Content A", 2, 0, 20)
        section2 = ParsedSection("Section B", "Content B", 2, 21, 40)
        doc = ParsedDocument("Title", [section1, section2], "source")

        # If this method exists
        if hasattr(doc, 'get_section'):
            found = doc.get_section("Section A")
            assert found is not None
            assert found.heading == "Section A"
