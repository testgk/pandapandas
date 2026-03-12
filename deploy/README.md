# 🌍 GeoChallenge Game - Deployment Guide

Complete deployment system for the interactive geography game with 3D globe, featuring 135+ cities and powered by GeoPandas/Pandas analytics.

## 🚀 Quick Start

### Windows
```bash
# Download and run the Windows deployer
curl -O https://raw.githubusercontent.com/testgk/pandapandas/master/deploy/deploy_windows.bat
deploy_windows.bat
```

### Linux/macOS
```bash
# Download and run the Linux deployer
curl -O https://raw.githubusercontent.com/testgk/pandapandas/master/deploy/deploy_linux.sh
chmod +x deploy_linux.sh
./deploy_linux.sh
```

## 📋 What the Deployment Scripts Do

### 1. **System Preparation**
- ✅ Verify Python 3.8+ and Git installation
- 📦 Install system dependencies (GDAL, GEOS, PROJ for geospatial operations)
- 🐍 Create isolated virtual environment

### 2. **Repository Management** 
- 📥 Clone repository from GitHub (`testgk/pandapandas`)
- 🔄 Update existing installation if already present
- 📁 Set up proper directory structure

### 3. **Dependency Installation**
- 📊 **Core**: `pandas`, `numpy`, `shapely`
- 🗺️ **Geospatial**: `geopandas`, `fiona`, `pyproj`, `rtree`
- 🎮 **3D Graphics**: `panda3d`
- 🌐 **Web Interface**: `folium`, `matplotlib`
- 📦 **Packaging**: `pyinstaller`

### 4. **Executable Creation**
- 🏗️ Generate standalone executable with PyInstaller
- 📝 Custom spec file for optimal packaging
- 🎯 Include all game assets and dependencies
- 💻 Cross-platform compatibility

### 5. **Launcher Setup**
- 🖱️ Easy-to-use run scripts
- 🐧 Desktop integration (Linux)
- ⚙️ Fallback to Python if executable fails
- 📱 User-friendly interface

## 🎮 Game Features Deployed

### **Interactive 3D Globe**
- 🌍 Real continent geometry from GeoPandas
- 🖱️ Click-to-guess on 3D Earth model
- 🔴 Visual markers for guesses and answers
- 📏 Distance calculations with great-circle formulas

### **Comprehensive Database**
- 🏙️ **135+ Cities** across 4 difficulty levels:
  - **Easy (25)**: Major capitals (NYC, London, Paris, Tokyo)
  - **Medium (44)**: Regional hubs (Barcelona, Stockholm, Istanbul) 
  - **Hard (32)**: Lesser-known capitals (Ulaanbaatar, Reykjavik)
  - **Expert (34)**: Obscure locations (Funafuti, Ngerulmud, Nuuk)

### **Professional Analytics**
- 📊 Real-time performance tracking with Pandas
- 📈 Statistical analysis of player accuracy
- 🎯 Adaptive difficulty based on performance
- 📋 Comprehensive game statistics

## 🖥️ System Requirements

### **Minimum Requirements**
- **OS**: Windows 10+ / Linux (Ubuntu 18.04+) / macOS 10.14+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Graphics**: OpenGL 3.3+ support

### **Recommended Requirements**
- **OS**: Windows 11 / Ubuntu 22.04+ / macOS 12+
- **Python**: 3.10+
- **RAM**: 8GB+
- **Storage**: 4GB free space
- **Graphics**: Dedicated GPU with OpenGL 4.0+

## 📁 Directory Structure After Deployment

```
geochallenge-game/
├── 🎮 run_geochallenge.[bat|sh]     # Main launcher
├── 🐍 venv/                         # Python virtual environment
├── 📊 p3d/                          # Core game files
│   ├── 🌍 globe_app.py             # 3D globe application
│   ├── 🎯 geo_challenge_game.py    # Game logic & 135 cities
│   ├── 📦 dist/                     # PyInstaller executables
│   ├── 🗺️ world_data/              # GeoPandas continent cache
│   ├── 🎨 gui/                      # User interface
│   └── ⚙️ settings/                 # Configuration files
├── 📝 run_geo_challenge.py          # Text-based version
├── 🌐 run_web_game.py               # Web-based version
└── 📋 requirements.txt              # Python dependencies
```

## 🔧 Advanced Configuration

### **Custom Installation Path**
```bash
# Windows
set DEPLOY_DIR=C:\MyGames\GeoChallenge
deploy_windows.bat

# Linux
DEPLOY_DIR=/opt/geochallenge ./deploy_linux.sh
```

### **Development Mode**
```bash
# Skip PyInstaller, run from source
SKIP_PYINSTALLER=1 ./deploy_linux.sh
```

### **Offline Installation**
1. Download repository as ZIP
2. Extract to desired location
3. Run deployment script from extracted folder

## 🐛 Troubleshooting

### **Common Issues**

#### **GeoPandas Installation Fails**
```bash
# Ubuntu/Debian
sudo apt install python3-dev libgdal-dev libgeos-dev libproj-dev

# CentOS/RHEL  
sudo yum install python3-devel gdal-devel geos-devel proj-devel

# macOS
brew install gdal geos proj
```

#### **Panda3D Graphics Issues**
```bash
# Install additional graphics libraries
sudo apt install libgl1-mesa-dev libglu1-mesa-dev freeglut3-dev
```

#### **PyInstaller Build Fails**
- ✅ Executable creation is optional - game runs from Python if needed
- 🔄 Try updating PyInstaller: `pip install --upgrade pyinstaller`
- 🐍 Use Python version as fallback

### **Performance Optimization**

#### **Large Dataset Loading**
- 🗂️ World data is cached after first load
- 🚀 Subsequent launches are much faster
- 💾 Cache stored in `p3d/world_data/`

#### **3D Graphics Performance**
- 🎮 Lower detail levels available in settings
- 🖥️ Ensure graphics drivers are updated
- ⚡ Use discrete GPU if available

## 🌐 Network Requirements

### **Initial Setup**
- 📥 Repository clone: ~50MB download
- 📦 Python packages: ~200MB total
- 🗺️ No additional data downloads required

### **Runtime**
- 🔌 **Offline capable** - no internet required after installation
- 🌍 All geographic data included locally
- 📊 Analytics stored locally

## 📞 Support

### **Getting Help**
- 📖 **Documentation**: Check README files in each directory
- 🐛 **Issues**: Report on GitHub repository
- 💬 **Community**: Discussions welcome

### **Logs and Debugging**
- 📝 Installation logs saved automatically
- 🔍 Debug mode: `python globe_launcher.py --debug`
- 📊 Game statistics: `p3d/game_stats.json`

## 🏆 Game Modes Available

After successful deployment, you can enjoy:

1. **🌍 3D Interactive Globe** - Click on the Earth model (Recommended)
2. **📝 Text-Based Game** - Enter coordinates manually  
3. **🌐 Web-Based Map** - Click on interactive web map

All modes feature the same 135+ city database with professional GeoPandas analytics!

---

**🎯 Ready to explore the world? Run the deployment script and start your geography adventure!**
