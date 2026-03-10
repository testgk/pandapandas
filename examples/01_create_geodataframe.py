from __future__ import annotations

import geopandas as gpd
from shapely.geometry import Point


def run() -> gpd.GeoDataFrame:
    """Create a simple GeoDataFrame from in-memory point data."""
    data = {
        "city": ["Berlin", "Paris", "Rome"],
        "lon": [13.4050, 2.3522, 12.4964],
        "lat": [52.5200, 48.8566, 41.9028],
    }
    geometry = [ Point( xy ) for xy in zip( data[ "lon" ], data[ "lat" ] ) ]
    gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")

    print("[01] Created GeoDataFrame:")
    print(gdf[["city", "geometry"]])
    print(f"CRS: {gdf.crs}")
    return gdf


if __name__ == "__main__":
    run()

