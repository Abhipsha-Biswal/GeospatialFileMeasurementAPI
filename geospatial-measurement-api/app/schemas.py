from typing import Optional, List
from pydantic import BaseModel


class FileInfo(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: Optional[str] = None
    status: str
    error: Optional[str] = None


class Measurement(BaseModel):
    feature_id: int
    geometry_type: str
    measurement: Optional[float] = None
    unit: Optional[str] = None


class MeasurementResponse(BaseModel):
    file_id: str
    measurements: List[Measurement]
