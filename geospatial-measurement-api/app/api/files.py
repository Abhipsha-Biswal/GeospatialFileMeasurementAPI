from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.database import get_connection
from app.schemas import FileInfo, MeasurementResponse
from app.services.file_processor import read_geospatial_file

router = APIRouter(prefix="/files", tags=["Files"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/", response_model=FileInfo, status_code=201)
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or "unknown"
    suffix = Path(filename).suffix.lower()

    if suffix not in {".kml", ".zip"}:
        raise HTTPException(
            status_code=400,
            detail="Only .kml and .zip (Shapefile) files are supported."
        )

    file_id = uuid4().hex
    saved_path = UPLOAD_DIR / f"{file_id}{suffix}"

    try:
        with saved_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        gdf = read_geospatial_file(saved_path)
        crs_text = gdf.crs.to_string() if gdf.crs else None

        conn = get_connection()
        conn.execute(
            """INSERT INTO files (id, filename, feature_count, crs, status, error)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (file_id, filename, len(gdf), crs_text, "COMPLETED", None),
        )
        conn.commit()
        conn.close()

        return FileInfo(
            id=file_id,
            filename=filename,
            feature_count=len(gdf),
            crs=crs_text,
            status="COMPLETED",
        )

    except Exception as exc:
        conn = get_connection()
        conn.execute(
            """INSERT INTO files (id, filename, feature_count, crs, status, error)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (file_id, filename, 0, None, "FAILED", str(exc)),
        )
        conn.commit()
        conn.close()

        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{file_id}/", response_model=FileInfo)
def get_file(file_id: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, filename, feature_count, crs, status, error FROM files WHERE id = ?",
        (file_id,),
    ).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="File not found.")

    return dict(row)


@router.get("/{file_id}/measurements/", response_model=MeasurementResponse)
def get_measurements(file_id: str):
    conn = get_connection()
    file_row = conn.execute(
        "SELECT * FROM files WHERE id = ?", (file_id,)
    ).fetchone()

    if file_row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="File not found.")

    if file_row["status"] != "COMPLETED":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"File processing status is {file_row['status']}."
        )

    existing = conn.execute(
        """SELECT feature_id, geometry_type, measurement, unit
           FROM measurements WHERE file_id = ? ORDER BY feature_id""",
        (file_id,),
    ).fetchall()

    if existing:
        conn.close()
        return {
            "file_id": file_id,
            "measurements": [dict(row) for row in existing],
        }

    conn.close()

    suffix = Path(file_row["filename"]).suffix.lower()
    path = UPLOAD_DIR / f"{file_id}{suffix}"

    try:
        gdf = read_geospatial_file(path)
        from app.services.measurement import calculate_measurements

        results = calculate_measurements(gdf)

        conn = get_connection()
        for item in results:
            conn.execute(
                """INSERT INTO measurements
                   (file_id, feature_id, geometry_type, measurement, unit)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    file_id,
                    item["feature_id"],
                    item["geometry_type"],
                    item["measurement"],
                    item["unit"],
                ),
            )
        conn.commit()
        conn.close()

        return {"file_id": file_id, "measurements": results}

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
