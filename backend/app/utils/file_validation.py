from fastapi import HTTPException
from .. import config

CHUNK = 1024 * 1024


async def save_edf(upload, dest):
    """Stream an upload to disk, enforcing extension, size and the EDF header signature."""
    name = (upload.filename or "").lower()
    if not name.endswith(".edf"):
        raise HTTPException(400, "Only .edf files are supported.")
    limit, size = config.MAX_UPLOAD_MB * CHUNK, 0
    first = True
    with open(dest, "wb") as f:
        while chunk := await upload.read(CHUNK):
            if first:
                if not chunk.startswith(b"0       "):       # EDF version field
                    f.close(); dest.unlink(missing_ok=True)
                    raise HTTPException(400, "File does not look like a valid EDF recording.")
                first = False
            size += len(chunk)
            if size > limit:
                f.close(); dest.unlink(missing_ok=True)
                raise HTTPException(413, f"File exceeds the {config.MAX_UPLOAD_MB} MB limit.")
            f.write(chunk)
    if size == 0:
        dest.unlink(missing_ok=True)
        raise HTTPException(400, "Empty file.")
    return size
