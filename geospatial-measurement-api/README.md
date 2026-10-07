# Geospatial File Measurement API

A FastAPI backend service for uploading KML files or zipped Shapefiles, extracting geospatial features, and calculating measurements.

## Assignment Coverage

The implementation provides:

- FastAPI backend
- `POST /api/files/` for KML and zipped Shapefile uploads
- Feature extraction
- Feature ID/index, geometry type, CRS, and attributes through GeoPandas processing
- Polygon area calculation
- LineString length calculation
- Point handling without measurement
- CRS-aware measurement calculation
- `GET /api/files/{id}/`
- `GET /api/files/{id}/measurements/`
- Automated API tests

## Tech Stack

- Python
- FastAPI
- GeoPandas
- Shapely
- PyProj
- Fiona
- SQLite
- Pytest

## Project Structure

```text
app/
├── api/
│   └── files.py
├── services/
│   ├── crs_handler.py
│   ├── file_processor.py
│   └── measurement.py
├── database.py
├── main.py
└── schemas.py
tests/
└── test_api.py
```

## Setup

### 1. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Geospatial packages can require GDAL/Fiona system support on some operating systems. If installation fails, use a current Python environment/conda environment with compatible GeoPandas dependencies.

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## API

### Upload

```http
POST /api/files/
```

Multipart form field:

```text
file
```

Supported:

- `.kml`
- `.zip` containing a Shapefile (`.shp` plus its supporting files)

Example using curl:

```bash
curl -X POST "http://127.0.0.1:8000/api/files/" \
  -F "file=@survey.kml"
```

Example response:

```json
{
  "id": "abc123",
  "filename": "survey.kml",
  "feature_count": 120,
  "crs": "EPSG:4326",
  "status": "COMPLETED",
  "error": null
}
```

### File Information

```http
GET /api/files/{id}/
```

Example:

```bash
curl "http://127.0.0.1:8000/api/files/abc123/"
```

### Measurements

```http
GET /api/files/{id}/measurements/
```

Example:

```json
{
  "file_id": "abc123",
  "measurements": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "measurement": 15234.67,
      "unit": "m²"
    },
    {
      "feature_id": 1,
      "geometry_type": "LineString",
      "measurement": 842.35,
      "unit": "m"
    },
    {
      "feature_id": 2,
      "geometry_type": "Point",
      "measurement": null,
      "unit": null
    }
  ]
}
```

## Architecture

### File-processing flow

1. Validate the uploaded extension.
2. Save the uploaded file using a generated unique ID.
3. Read KML directly or extract the ZIP and locate the `.shp` file.
4. Load the data with GeoPandas.
5. Store file metadata in SQLite.
6. Calculate measurements when the measurements endpoint is requested.
7. Store calculated measurements to avoid repeating the calculation.

### Measurement flow

Polygon and MultiPolygon geometries use `.area`.

LineString and MultiLineString geometries use `.length`.

Points and MultiPoints do not require a measurement.

Unsupported geometry types are returned with `measurement: null` instead of causing the API to crash.

### CRS handling

Area and length must not be calculated directly from longitude/latitude degrees.

When the source CRS is geographic, the service uses GeoPandas' `estimate_utm_crs()` to select a suitable projected CRS and transforms the geometries before calculating measurements.

If a file has no CRS, the service fails safely rather than producing potentially misleading measurements.

## Design Decisions

### Why FastAPI?

FastAPI provides:

- Simple API routing
- Automatic OpenAPI documentation
- Pydantic response validation
- Easy multipart file uploads
- Good support for modern Python applications

### Why GeoPandas?

GeoPandas provides a high-level interface for reading geospatial formats and working with CRS-aware geometries.

### Why SQLite?

The assignment requires file information and measurements but does not require a production database. SQLite keeps the project simple and easy to run locally.

For production, PostgreSQL with PostGIS would be a stronger alternative.

### Why calculate measurements on demand?

Uploading and validating the file happens immediately. Measurement calculation is performed when requested and then cached in SQLite. This keeps the upload endpoint straightforward and avoids duplicate calculations.

## Error Handling

The API rejects unsupported extensions and malformed/invalid geospatial files with HTTP 400 responses.

Missing file IDs return HTTP 404.

Files without CRS are rejected during measurement calculation because the service cannot safely determine metric area or distance.

## Testing

Run:

```bash
pytest
```

The included tests cover the root endpoint and unsupported file validation.

## Learning

This project demonstrates practical use of:

- FastAPI API design
- Multipart file uploads
- GeoPandas
- Shapely geometry handling
- CRS transformation
- Geospatial measurement
- SQLite persistence
- Automated API testing
- API documentation with OpenAPI

## Future Scope

Possible improvements include:

- PostgreSQL/PostGIS
- Background processing for large files
- Celery or another task queue
- File-size limits
- Authentication and authorization
- Cloud object storage
- More geospatial formats
- Detailed attribute responses
- Measurement units such as km and hectares
- Docker deployment
- More comprehensive integration tests
- Automatic cleanup of uploaded files
- Rate limiting and production monitoring

## GitHub Submission

Create a public repository and push the project:

```bash
git init
git add .
git commit -m "Build geospatial measurement API"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```
