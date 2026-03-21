# Frontend Documentation

Documentation for the GeoChallenge desktop (Panda3D) and web applications.

## 📚 Available Documentation

**[README_DATABASE.md](./README_DATABASE.md)**
- Desktop app database setup guide
- How to launch with local or remote database
- Database features and troubleshooting
- Quick reference for launch scripts

## 🎮 Desktop App (Panda3D)

The desktop application is built with Panda3D and supports multiple modes:

### Launch Modes

**Game Mode (Default):**
```bash
cd geochallenge-frontend
python3 p3d/globe_launcher.py
# or
./launch_desktop_local.sh    # with local database
./launch_desktop_remote.sh   # with remote database
```

**Globe Viewer Mode:**
```bash
python3 p3d/globe_launcher.py --mode globe
```

**Android/Touch Mode:**
```bash
python3 p3d/globe_launcher.py --mode android
```

### Database Configuration

The desktop app can connect to:

1. **Local Database** (Docker PostgreSQL)
   - Run: `./launch_desktop_local.sh`
   - Requires: Docker running with `docker-compose up -d`

2. **Remote Database** (Render.com)
   - Run: `./launch_desktop_remote.sh`
   - Requires: Internet connection

3. **No Database** (Offline mode)
   - Run: `python3 p3d/globe_launcher.py`
   - Works without database (no leaderboard)

See [README_DATABASE.md](./README_DATABASE.md) for detailed setup.

## 🌐 Web App

The web application is located in the `web/` directory.

### Structure
```
geochallenge-frontend/
├── p3d/                    # Panda3D desktop app
│   ├── globe_launcher.py   # Main entry point
│   ├── globe_app.py        # Main application
│   ├── game/               # Game logic
│   ├── gui/                # GUI components
│   └── world_data/         # Geographic data
├── web/                    # Web application
│   ├── index.html
│   ├── css/
│   └── js/
├── launch_desktop_local.sh    # Local DB launcher
├── launch_desktop_local.bat   # Windows local
├── launch_desktop_remote.sh   # Remote DB launcher
└── launch_desktop_remote.bat  # Windows remote
```

## 🚀 Quick Start

### First Time Setup

**1. Install Dependencies:**
```bash
cd geochallenge-frontend/p3d
pip install -r requirements.txt
```

**2. Choose Database Option:**

**Option A: Local Database**
```bash
cd ../../geochallenge-backend
docker-compose up -d
cd ../geochallenge-frontend
./launch_desktop_local.sh
```

**Option B: Remote Database**
```bash
# Already configured for Render.com
./launch_desktop_remote.sh
```

**Option C: No Database**
```bash
cd p3d
python3 globe_launcher.py
```

### Running the App

**Linux/Mac:**
```bash
# Local database
./launch_desktop_local.sh

# Remote database
./launch_desktop_remote.sh

# No database
cd p3d && python3 globe_launcher.py
```

**Windows:**
```cmd
# Local database
launch_desktop_local.bat

# Remote database
launch_desktop_remote.bat

# No database
cd p3d
python globe_launcher.py
```

## 🎯 Features

### With Database Connected:
✅ Global leaderboard
✅ Save scores across sessions
✅ Compare with other players
✅ Database statistics
✅ Persistent game history

### Without Database:
✅ Full gameplay
✅ Local session statistics
✅ All game features
❌ No global leaderboard
❌ No cross-device scores

## 🔧 Configuration

### Import Structure

The desktop app uses relative imports:

```python
# Correct (relative imports)
from .game_controller import GameController
from ..gui.game_gui_controller import GameGuiController

# Incorrect (absolute imports - don't use)
from game.game_controller import GameController
```

All imports have been fixed to use proper relative imports.

### Database Connection

Database connection reads from environment variables:

```bash
export DB_HOST=localhost              # or remote host
export DB_PORT=5432
export DB_NAME=geochallenge_db
export DB_USER=geochallenge
export DB_PASSWORD=geochallenge_secret
```

The launch scripts set these automatically.

## 📖 Related Documentation

- [Database Configuration](./README_DATABASE.md) - Detailed database setup
- [Root Documentation](../../docs/) - Database guides
- [Backend Documentation](../../geochallenge-backend/docs/) - API documentation
- [Scripts](../../scripts/README.md) - Utility scripts

## 🐛 Troubleshooting

### Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'game'`

**Solution:**
- All imports have been fixed to use relative imports
- Run from the correct directory
- Check Python path includes the project root

### Database Connection Fails

**Symptom:** "DB Error: connection refused"

**Solutions:**

**For Local Database:**
```bash
cd geochallenge-backend
docker-compose up -d
```

**For Remote Database:**
- Check internet connection
- Verify credentials in launch script
- Test: `python3 ../../scripts/test_remote_connection.py`

### App Won't Start

**Check:**
1. Python version: `python3 --version` (need 3.12+)
2. Dependencies: `pip install -r p3d/requirements.txt`
3. Panda3D installed: `python3 -c "import panda3d"`

## 🆘 Need Help?

- **Database setup:** [README_DATABASE.md](./README_DATABASE.md)
- **Import errors:** All fixed to use relative imports
- **Connection issues:** [../../docs/DESKTOP_APP_DATABASE_CONFIG.md](../../docs/DESKTOP_APP_DATABASE_CONFIG.md)
- **Scripts:** [../../scripts/README.md](../../scripts/README.md)

## 💡 Development

### Project Structure

```
p3d/
├── game/
│   ├── game_controller.py      # Main game logic
│   ├── geo_challenge_game.py   # Challenge system
│   └── game_markers.py         # Visual markers
├── gui/
│   ├── game_gui_controller.py  # Game GUI
│   ├── globe_gui_controller.py # Globe GUI
│   └── android_controller.py   # Touch controls
├── interfaces/
│   └── i_globe_application.py  # Interface definition
├── settings/
│   └── gui_settings_manager.py # GUI configuration
└── world_data/
    └── continent_country_map.py # Geographic data
```

### Adding Features

1. Game logic → `game/game_controller.py`
2. GUI elements → `gui/game_gui_controller.py`
3. Visual markers → `game/game_markers.py`
4. Settings → `settings/gui_settings_manager.py`

### Testing

```bash
# Run the app in different modes
python3 p3d/globe_launcher.py --mode game
python3 p3d/globe_launcher.py --mode globe
python3 p3d/globe_launcher.py --mode android
```
