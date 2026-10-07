from typing import Dict, Any
import geopandas as gpd
from app.services.crs_handler import prepare_for_measurement


def calculate_measurements(gdf: gpd.GeoDataFrame):
    projected = prepare_for_measurement(gdf)
    results = []

    for index, row in projected.iterrows():
        geometry = row.geometry
        geometry_type = geometry.geom_type if geometry is not None else "Unknown"

        measurement = None
        unit = None

        if geometry_type == "Polygon" or geometry_type == "MultiPolygon":
            measurement = float(geometry.area)
            unit = "m²"
        elif geometry_type == "LineString" or geometry_type == "MultiLineString":
            measurement = float(geometry.length)
            unit = "m"
        elif geometry_type == "Point" or geometry_type == "MultiPoint":
            measurement = None
            unit = None

        results.append({
            "feature_id": int(index) if isinstance(index, int) else len(results),
            "geometry_type": geometry_type,
            "measurement": measurement,
            "unit": unit,
        })

    return results
