"""
Shared CLI helpers for scripts.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, List


def ensure_repo_root_on_path(script_file: str | Path) -> None:
    """Ensure repo root is importable for app modules."""
    repo_root = Path(script_file).resolve().parent.parent
    sys.path.insert(0, str(repo_root))


def collect_exam_files(exam: str | None, exam_dir: str | None) -> List[Path]:
    """Collect exam JSON files from a file or directory."""
    if exam:
        return [Path(exam)]

    if not exam_dir:
        return []

    exam_path = Path(exam_dir)
    return list(exam_path.glob('exam_*.json'))
