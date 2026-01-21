"""
PDF conversion helpers.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from app.utils.preprocess import sanitize_filename, text_to_markdown


def convert_pdf_to_markdown(pdf_path: Path, output_dir: Path) -> Path:
    """
    Convert a PDF file to a markdown document using pdftotext.
    """
    title = pdf_path.stem
    safe_stem = sanitize_filename(title) or "document"
    markdown_path = output_dir / f"{safe_stem}.md"

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)

    try:
        subprocess.run(["pdftotext", str(pdf_path), str(tmp_path)], check=True)
        text = tmp_path.read_text(encoding="utf-8", errors="ignore")
        markdown_path.write_text(text_to_markdown(text, title), encoding="utf-8")
    finally:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass

    return markdown_path
