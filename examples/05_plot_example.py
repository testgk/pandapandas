from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point


def run(output_path: str = "outputs/points_plot.png") -> Path:
    """Create a simple point plot and save it to disk."""
    gdf = gpd.GeoDataFrame(
        {"label": ["P1", "P2", "P3"]},
        geometry=[Point(0, 0), Point(1, 2), Point(2, 1)],
        crs="EPSG:4326",
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(5, 4))
    gdf.plot(ax=ax, color="tab:blue", markersize=60)
    ax.set_title("GeoPandas Point Plot")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)

    print(f"[05] Saved plot to: {out.resolve()}")
    return out


if __name__ == "__main__":
    run()

