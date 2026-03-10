# 3D Globe with Panda3D + GeoPandas

Interactive 3D globe showing world continents using Panda3D and GeoPandas.

## Features

- 3D sphere with procedural geometry
- Real continent data from GeoPandas built-in world dataset
- Color-coded continents
- Interactive camera controls (orbit, zoom)
- Auto-rotation when idle

## Setup

```powershell
cd D:\geopandas\p3d
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
cd D:\geopandas\p3d
.\venv\Scripts\Activate.ps1
python main.py
```

## Controls

- **Mouse drag**: Orbit camera around globe
- **Mouse wheel**: Zoom in/out
- **Auto-rotation**: Globe rotates when not manually controlling

## Implementation

- Uses GeoPandas `naturalearth_lowres` dataset for continent boundaries
- Converts geographic coordinates (lat/lon) to 3D sphere surface coordinates
- Creates procedural sphere mesh with Panda3D's geometry system
- Projects continent polygons onto sphere surface with slight elevation to avoid z-fighting

The globe automatically loads world continent data and displays each continent in a different color.
