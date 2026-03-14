from pathlib import Path
import tempfile


TEMP_DIR = Path(tempfile.gettempdir()) / "report_export_api"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_CHUNK_SIZE = 1024 * 1024
MAX_CONCURRENT_EXPORTS = 2
SQLITE_COMMIT_EVERY = 1000
