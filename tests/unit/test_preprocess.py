from app.utils.preprocess import sanitize_filename, text_to_markdown


def test_sanitize_filename_replaces_spaces_and_strips():
    assert sanitize_filename("  file name  ") == "file_name"


def test_text_to_markdown_adds_title_and_paragraphs():
    text = "Line one.\\n\\nLine two."
    md = text_to_markdown(text, title="Doc")
    assert md.startswith("# Doc")
    assert "Line one." in md
    assert "Line two." in md
