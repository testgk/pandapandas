"""
PyInstaller Hook for GeoPandas Globe Application
Ensures all necessary data files and modules are included
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files from critical packages
datas = []

# Panda3D data files
try:
    datas += collect_data_files('panda3d')
except:
    pass

# GeoPandas data files
try:
    datas += collect_data_files('geopandas')
except:
    pass

# Shapely data files  
try:
    datas += collect_data_files('shapely')
except:
    pass

# Fiona data files (GDAL drivers)
try:
    datas += collect_data_files('fiona')
except:
    pass

# PyProj data files (projection data)
try:
    datas += collect_data_files('pyproj')
except:
    pass

# Collect submodules that might be missed
hiddenimports = []

# Panda3D submodules
try:
    hiddenimports += collect_submodules('panda3d')
except:
    pass

# Direct submodules (Panda3D's framework)
try:
    hiddenimports += collect_submodules('direct')
except:
    pass

# GeoPandas submodules
try:
    hiddenimports += collect_submodules('geopandas')
except:
    pass

# Specific modules that are commonly missed
hiddenimports += [
    'panda3d.core',
    'direct.showbase.ShowBase',
    'direct.gui.DirectGui',
    'direct.gui.OnscreenText',
    'direct.gui.DirectButton',
    'shapely.geometry',
    'shapely.ops',
    'fiona.drvsupport',
    'fiona._shim',
    'fiona.ogrext',
    'pyproj.crs',
    'pyproj.transformer',
]
