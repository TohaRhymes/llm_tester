#!/usr/bin/env python3
"""
Preprocess medical PDFs and ML markdown materials into research-ready datasets.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Ensure repo root is on sys.path for app imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils.preprocess import sanitize_filename, text_to_markdown


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from a PDF using pdftotext."""
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def preprocess_medical_pdfs(source_dir: Path, output_dir: Path, overwrite: bool) -> int:
    """Convert medical PDFs into markdown files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for pdf_path in sorted(source_dir.glob("*.pdf")):
        stem = sanitize_filename(pdf_path.stem)
        output_path = output_dir / f"{stem}.md"
        if output_path.exists() and not overwrite:
            continue

        text = extract_pdf_text(pdf_path)
        markdown = text_to_markdown(text, title=pdf_path.stem)
        output_path.write_text(markdown, encoding="utf-8")
        count += 1

    return count


def copy_ml_materials(source_dir: Path, output_dir: Path, overwrite: bool) -> int:
    """Copy ML markdown materials to the used dataset directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for md_path in sorted(source_dir.glob("*.md")):
        target = output_dir / md_path.name
        if target.exists() and not overwrite:
            continue
        shutil.copy2(md_path, target)
        count += 1

    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess medical PDFs and ML markdown materials.")
    parser.add_argument("--medical-source", type=Path, default=Path("examples/raw/medical"))
    parser.add_argument("--medical-output", type=Path, default=Path("examples/used/medical"))
    parser.add_argument("--ml-source", type=Path, default=Path("examples/raw/ml"))
    parser.add_argument("--ml-output", type=Path, default=Path("examples/used/ml"))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    medical_count = preprocess_medical_pdfs(args.medical_source, args.medical_output, args.overwrite)
    ml_count = copy_ml_materials(args.ml_source, args.ml_output, args.overwrite)

    print(f"Medical PDFs processed: {medical_count}")
    print(f"ML markdown copied: {ml_count}")


if __name__ == "__main__":
    main()
