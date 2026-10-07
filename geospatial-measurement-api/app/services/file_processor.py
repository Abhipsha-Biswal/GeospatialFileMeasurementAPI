from pathlib import Path
import tempfile
import zipfile
import geopandas as gpd


ALLOWED_EXTENSIONS = {".kml", ".zip"}


def _find_shapefile(directory: Path) -> Path:
    shp_files = list(directory.rglob("*.shp"))
    if not shp_files:
        raise ValueError("ZIP file does not contain a .shp file.")
    return shp_files[0]


def read_geospatial_file(file_path: Path) -> gpd.GeoDataFrame:
    suffix = file_path.suffix.lower()

    if suffix == ".kml":
        # Fiona/GDAL may require this driver to be explicitly enabled.
        try:
            gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
        except Exception:
            pass
        return gpd.read_file(file_path, driver="KML")

    if suffix == ".zip":
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            with zipfile.ZipFile(file_path, "r") as archive:
                archive.extractall(temp_path)

            shp_path = _find_shapefile(temp_path)

            # Read before TemporaryDirectory is removed.
            return gpd.read_file(shp_path)

    raise ValueError("Unsupported file type. Upload a .kml or .zip Shapefile.")
