from __future__ import annotations

import geopandas as gpd
from shapely.geometry import Point, box


def run() -> gpd.GeoDataFrame:
    """Join points to polygons using a spatial predicate."""
    neighborhoods = gpd.GeoDataFrame(
        {"zone": ["West", "East"]},
        geometry=[box(0, 0, 5, 10), box(5, 0, 10, 10)],
        crs="EPSG:4326",
    )

    shops = gpd.GeoDataFrame(
        {"shop": ["S1", "S2", "S3"]},
        geometry=[Point(2, 2), Point(7, 3), Point(11, 4)],
        crs="EPSG:4326",
    )

    joined = gpd.sjoin(shops, neighborhoods, predicate="within", how="left")

    print("[04] Spatial join result:")
    print(joined[["shop", "zone"]])
    return joined


if __name__ == "__main__":
    run()

