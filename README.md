# GeoPandas Examples

Small, runnable GeoPandas examples using synthetic data (no downloads required).

## Files

- `examples/01_create_geodataframe.py`: create a `GeoDataFrame` from points.
- `examples/02_reproject_crs.py`: reproject geometries between CRS.
- `examples/03_buffer_and_area.py`: buffer geometries and compute area.
- `examples/04_spatial_join.py`: perform a spatial join.
- `examples/05_plot_example.py`: plot points and save PNG output.
- `run_examples.py`: runs all examples in sequence.

## Setup (PowerShell)

```powershell
cd D:\geopandas
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run

```powershell
cd D:\geopandas
.\.venv\Scripts\Activate.ps1
python run_examples.py
```

## Notes

- `examples/04_spatial_join.py` uses `geopandas.sjoin(...)`; depending on your install, GeoPandas may use `rtree` or another spatial index backend.
- Plot output is written to `outputs/points_plot.png`.

