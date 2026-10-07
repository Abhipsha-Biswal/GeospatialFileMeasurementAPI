import geopandas as gpd


def prepare_for_measurement(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Geographic CRS values such as EPSG:4326 use degrees, so they must not
    be used directly for area/length calculations.

    For geographic data, GeoPandas' estimate_utm_crs selects a suitable
    projected CRS based on the dataset location.
    """
    if gdf.crs is None:
        raise ValueError("Input file has no CRS; measurements cannot be calculated safely.")

    if gdf.crs.is_geographic:
        projected_crs = gdf.estimate_utm_crs()
        if projected_crs is None:
            raise ValueError("Could not determine a suitable projected CRS.")
        return gdf.to_crs(projected_crs)

    return gdf
