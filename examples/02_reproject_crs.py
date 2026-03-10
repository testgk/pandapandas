from __future__ import annotations

import geopandas as gpd
from shapely.geometry import Point


def run() -> gpd.GeoDataFrame:
    """Reproject point data from WGS84 to Web Mercator."""
    base = gpd.GeoDataFrame(
        {"name": ["A", "B"], "lon": [0.0, 10.0], "lat": [0.0, 10.0]},
        geometry=[Point(0.0, 0.0), Point(10.0, 10.0)],
        crs="EPSG:4326",
    )
    projected = base.to_crs("EPSG:3857")

    print("[02] Reprojected to EPSG:3857:")
    print(projected[["name", "geometry"]])
    print(f"Original CRS: {base.crs}; New CRS: {projected.crs}")
    return projected


if __name__ == "__main__":
    run()

