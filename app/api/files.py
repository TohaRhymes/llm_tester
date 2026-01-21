"""
File upload and management endpoints.
"""
import os
import subprocess
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from app.config import settings
from app.utils.path import safe_join
from app.utils.pdf import convert_pdf_to_markdown
from app.utils.preprocess import sanitize_filename

router = APIRouter()

# Directory for uploaded files
UPLOAD_DIR = Path(settings.uploads_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Security: Maximum file upload size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


@router.post("/api/upload", tags=["files"])
async def upload_file(
    file: UploadFile = File(...),
    name: str | None = Query(None),
):
    """
    Upload a Markdown file for exam generation.

    Args:
        file: Markdown file (.md)

    Returns:
        File information and path
    """
    # Validate file extension
    is_markdown = file.filename.endswith('.md')
    is_pdf = file.filename.endswith('.pdf')
    if not (is_markdown or is_pdf):
        raise HTTPException(
            status_code=400,
            detail="Only .md (Markdown) or .pdf files are allowed"
        )

    custom_name = sanitize_filename(name or "")
    if custom_name:
        if is_markdown:
            filename = f"{custom_name}.md"
        else:
            filename = f"{custom_name}.pdf"
    else:
        filename = file.filename

    # Save file
    try:
        file_path = safe_join(UPLOAD_DIR, filename)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename")

    try:
        content = await file.read()

        # Security: Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024):.0f}MB"
            )

        with open(file_path, 'wb') as f:
            f.write(content)

        if is_pdf:
            try:
                markdown_path = convert_pdf_to_markdown(file_path, UPLOAD_DIR)
            except FileNotFoundError:
                raise HTTPException(
                    status_code=500,
                    detail="pdftotext not available; install poppler-utils to enable PDF parsing"
                )
            except subprocess.CalledProcessError as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse PDF: {exc}"
                )

            return {
                "filename": filename,
                "path": str(file_path),
                "size": len(content),
                "markdown_filename": markdown_path.name,
                "markdown_path": str(markdown_path),
                "message": "PDF uploaded and converted successfully"
            }

        return {
            "filename": filename,
            "path": str(file_path),
            "size": len(content),
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )


@router.get("/api/files", tags=["files"])
async def list_files():
    """
    List all uploaded Markdown and PDF files.

    Returns:
        List of uploaded files with metadata
    """
    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if not file_path.is_file():
            continue
        if file_path.suffix not in {".md", ".pdf"}:
            continue
        stat = file_path.stat()
        files.append({
            "filename": file_path.name,
            "path": str(file_path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "file_type": "markdown" if file_path.suffix == ".md" else "pdf",
        })

    files = sorted(files, key=lambda item: item["filename"].lower())
    return {"files": files, "count": len(files)}


@router.get("/api/files/{filename}", tags=["files"])
async def get_file_content(filename: str):
    """
    Get content of an uploaded file.

    Args:
        filename: Name of the file

    Returns:
        File content
    """
    try:
        file_path = safe_join(UPLOAD_DIR, filename)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not (filename.endswith(".md") or filename.endswith(".pdf")):
        raise HTTPException(
            status_code=400,
            detail="Only .md or .pdf files can be read"
        )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' not found"
        )

    if file_path.suffix == ".pdf":
        try:
            content = file_path.read_bytes()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read file: {str(e)}"
            )

        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"{file_path.name}\""},
        )

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "filename": filename,
            "content": content,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read file: {str(e)}"
        )


@router.get("/api/exams", tags=["exams"])
async def list_exams(
    sort_by: str = Query("created", description="Sort by created|size|exam_id"),
    order: str = Query("desc", description="Sort order asc|desc"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """
    List all generated exams.

    Returns:
        List of exams with metadata
    """
    exams = []
    out_dir = Path(settings.output_dir)

    for exam_file in out_dir.glob("exam_*.json"):
        stat = exam_file.stat()
        exam_id = exam_file.stem.replace("exam_", "")

        exams.append({
            "exam_id": exam_id,
            "filename": exam_file.name,
            "path": str(exam_file),
            "size": stat.st_size,
            "created": stat.st_mtime
        })

    sort_key_map = {
        "created": lambda x: x["created"],
        "size": lambda x: x["size"],
        "exam_id": lambda x: x["exam_id"]
    }
    if sort_by not in sort_key_map:
        raise HTTPException(status_code=400, detail="Invalid sort_by")

    reverse = order.lower() == "desc"
    exams = sorted(exams, key=sort_key_map[sort_by], reverse=reverse)

    total = len(exams)
    total_pages = (total + page_size - 1) // page_size if page_size else 1
    start = (page - 1) * page_size
    end = start + page_size
    exams_page = exams[start:end]

    return {
        "exams": exams_page,
        "count": len(exams_page),
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/api/exams/{exam_id}", tags=["exams"])
async def get_exam(exam_id: str):
    """
    Get a specific exam by ID.

    Args:
        exam_id: Exam identifier

    Returns:
        Full exam data
    """
    import json

    try:
        exam_file = safe_join(Path(settings.output_dir), f"exam_{exam_id}.json")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam id")

    if not exam_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Exam '{exam_id}' not found"
        )

    try:
        with open(exam_file, 'r', encoding='utf-8') as f:
            exam_data = json.load(f)

        return exam_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load exam: {str(e)}"
        )
