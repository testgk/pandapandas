# GeoPandas Globe - Build Instructions

## Building Standalone Executables

This project supports multiple deployment methods. **Nuitka is now the recommended approach** as it provides better performance and handles dependencies more reliably than PyInstaller.

## Recommended: Nuitka Build (Better Performance)

Nuitka compiles Python to C++ for superior performance and more reliable dependency handling.

### Windows Build with Nuitka

1. **Open Command Prompt or PowerShell as Administrator**
2. **Navigate to the project directory:**
   ```cmd
   cd D:\geopandas
   ```
3. **Run the Nuitka build script:**
   ```cmd
   build_nuitka_windows.bat
   ```

The script will:
- Install Nuitka automatically
- Compile the application to optimized C++
- Create `p3d\GeoPandas-Globe-Nuitka.exe`
- **Result:** Faster execution, smaller size, better compatibility

### Linux Build with Nuitka

1. **Open Terminal**
2. **Navigate to the project directory:**
   ```bash
   cd /path/to/geopandas
   ```
3. **Make the build script executable:**
   ```bash
   chmod +x build_nuitka_linux.sh
   ```
4. **Run the Nuitka build script:**
   ```bash
   ./build_nuitka_linux.sh
   ```

### Manual Nuitka Build (Advanced)

For custom configurations:

#### Windows:
```cmd
cd p3d
pip install nuitka
nuitka --onefile --follow-imports --output-filename=GeoPandas-Globe-Nuitka.exe globe_app.py
```

#### Linux:
```bash
cd p3d
pip3 install nuitka
python3 -m nuitka --onefile --follow-imports --output-filename=geopandas-globe-nuitka globe_app.py
```

## Alternative: PyInstaller Build

If Nuitka doesn't work on your system, PyInstaller is available as a fallback.

### Windows Build with PyInstaller

1. **Navigate to the p3d directory:**
   ```cmd
   cd D:\geopandas\p3d
   ```
2. **Run the PyInstaller build script:**
   ```cmd
   build_windows.bat
   ```

### Linux Build with PyInstaller

1. **Navigate to the p3d directory:**
   ```bash
   cd /path/to/geopandas/p3d
   ```
2. **Run the PyInstaller build script:**
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```

### Build Outputs

#### Windows:
- **Executable:** `dist\GeoPandas-Globe-Windows.exe`
- **Size:** ~200-500 MB (includes all dependencies)
- **Requirements:** None (standalone)

#### Linux:
- **Executable:** `dist/geopandas-globe-linux`
- **Size:** ~200-500 MB (includes all dependencies)  
- **Requirements:** None (standalone, includes all system libraries)

### Distribution

The generated executables are completely standalone and can be:
- Copied to any compatible system
- Run without Python installation
- Distributed without dependency concerns
- Executed directly by double-clicking (Windows) or `./executable` (Linux)

### Advantages over Docker

✅ **No Docker required:** Direct native execution
✅ **Smaller footprint:** No container overhead
✅ **Faster startup:** No container initialization
✅ **Native performance:** Direct system access
✅ **User-friendly:** Double-click to run
✅ **Easy distribution:** Single file deployment

### Troubleshooting

**Build Fails:**
- Ensure all dependencies are installed: `pip install -r requirements_pyinstaller.txt`
- Check Python version: Must be 3.8+
- Verify disk space: Build requires ~2GB temporary space

**Runtime Issues:**
- Missing libraries: The executable should be fully self-contained
- File permissions (Linux): Ensure executable has proper permissions
- Graphics issues: Ensure system has proper OpenGL drivers

**Performance:**
- First run may be slower as files are extracted
- Subsequent runs should be at native speed
- Large executable size is normal due to bundled dependencies

### File Structure After Build

```
p3d/
├── globe_app.py                    # Main application
├── globe_windows.spec             # Windows PyInstaller config
├── globe_linux.spec               # Linux PyInstaller config
├── build_windows.bat              # Windows build script
├── build_linux.sh                 # Linux build script
├── requirements_pyinstaller.txt   # PyInstaller dependencies
├── hook-globe_app.py              # PyInstaller hook for missing modules
├── dist/                          # Build output directory
│   ├── GeoPandas-Globe-Windows.exe # Windows executable
│   └── geopandas-globe-linux      # Linux executable
└── build/                         # Temporary build files
```

### Next Steps

1. Run the appropriate build script for your platform
2. Test the generated executable
3. Distribute the single executable file
4. No more Docker containers needed!

The PyInstaller approach provides a much simpler deployment model while maintaining all the functionality of the original GeoPandas Globe application.
