from __future__ import annotations

import geopandas as gpd
from shapely.geometry import Point


def run() -> gpd.GeoDataFrame:
    """Create metric buffers and compute area in square meters."""
    points = gpd.GeoDataFrame(
        {"id": [1, 2], "x": [0, 1500], "y": [0, 1500]},
        geometry=[Point(0, 0), Point(1500, 1500)],
        crs="EPSG:3857",
    )

    buffered = points.copy()
    buffered["geometry"] = buffered.geometry.buffer(1000)
    buffered["area_m2"] = buffered.geometry.area.round(2)

    print("[03] Buffered polygons and areas:")
    print(buffered[["id", "area_m2"]])
    return buffered


if __name__ == "__main__":
    run()

