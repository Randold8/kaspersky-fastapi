import asyncio
from pathlib import Path
import uuid

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.concurrency import export_slot
from app.core.config import TEMP_DIR, UPLOAD_CHUNK_SIZE
from app.services.export_report import ExportReportService


router = APIRouter(prefix="/public/report", tags=["report"])


def remove_file(path: Path) -> None:
    path.unlink(missing_ok=True)


def is_text_file(upload_file: UploadFile) -> bool:
    if upload_file.content_type == "text/plain":
        return True
    if upload_file.filename and upload_file.filename.lower().endswith(".txt"):
        return True
    return False


async def save_upload_to_temp(upload_file: UploadFile) -> Path:
    temp_path = TEMP_DIR / f"{uuid.uuid4().hex}.txt"

    with temp_path.open("wb") as buffer:
        while chunk := await upload_file.read(UPLOAD_CHUNK_SIZE):
            buffer.write(chunk)

    await upload_file.close()
    return temp_path


@router.post("/export")
async def export_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if not is_text_file(file):
        raise HTTPException(status_code=400, detail="Only text files are supported")

    source_path = await save_upload_to_temp(file)

    try:
        service = ExportReportService()

        try:
            with export_slot():
                result = await asyncio.to_thread(service.export, source_path)
        except RuntimeError as exc:
            if str(exc) == "export_limit_reached":
                raise HTTPException(
                    status_code=429,
                    detail="Too many export requests. Try again later.",
                ) from exc
            raise

        background_tasks.add_task(remove_file, source_path)
        background_tasks.add_task(remove_file, result.output_path)

        return FileResponse(
            path=result.output_path,
            filename=result.filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception:
        remove_file(source_path)
        raise
