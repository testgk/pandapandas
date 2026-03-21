# Desktop App Database Setup

## Quick Start

The desktop app can work with **LOCAL** or **REMOTE** database (or no database at all).

### Current Setup: LOCAL DATABASE (Default)

The app connects to `localhost:5432` by default.

## Launch Scripts

Use these scripts to easily launch the app with different database configurations:

### Linux/Mac:

```bash
# Local database (docker-compose)
./launch_desktop_local.sh

# Remote database (AWS, Render, etc.)
./launch_desktop_remote.sh  # Edit this file first with your credentials
```

### Windows:

```cmd
# Local database (docker-compose)
launch_desktop_local.bat

# Remote database (AWS, Render, etc.)
launch_desktop_remote.bat  # Edit this file first with your credentials
```

## Setup Instructions

### Option 1: Local Database (Recommended for Development)

**1. Start PostgreSQL:**
```bash
cd ../geochallenge-backend
docker-compose up -d
```

**2. Launch desktop app:**
```bash
./launch_desktop_local.sh
```

**3. Stop PostgreSQL when done:**
```bash
cd ../geochallenge-backend
docker-compose down
```

### Option 2: Remote Database (For Production)

**1. Edit the remote launch script:**

**Linux/Mac:** Edit `launch_desktop_remote.sh`
```bash
export DB_HOST="your-database.amazonaws.com"
export DB_PORT="5432"
export DB_NAME="geochallenge_db"
export DB_USER="your_username"
export DB_PASSWORD="your_password"
```

**Windows:** Edit `launch_desktop_remote.bat`
```batch
set DB_HOST=your-database.amazonaws.com
set DB_PORT=5432
set DB_NAME=geochallenge_db
set DB_USER=your_username
set DB_PASSWORD=your_password
```

**2. Launch the app:**
```bash
./launch_desktop_remote.sh  # Linux/Mac
launch_desktop_remote.bat   # Windows
```

### Option 3: No Database (Works Offline)

The app works without a database - you just won't have:
- Global leaderboard
- Cross-device stats
- Database statistics

Just run normally:
```bash
cd p3d
python3 globe_launcher.py
```

## Database Features

When database is connected:

✅ **DB Stats Button** - View global leaderboard and statistics
✅ **Save scores** - Your scores are saved to database
✅ **Leaderboard** - Compare your performance with other players

When database is NOT connected:

✅ **Local gameplay** - Everything works normally
✅ **Session stats** - View your current session statistics
❌ **No leaderboard** - Can't view or save global scores

## Troubleshooting

### "DB Error: connection refused"

**Local Database:**
```bash
cd geochallenge-backend
docker-compose up -d
```

**Remote Database:**
- Check your credentials are correct
- Verify the remote database is running
- Check firewall allows your IP

### "DB Error: authentication failed"

Your credentials are wrong. Double-check:
- DB_USER
- DB_PASSWORD
- DB_NAME

### Database button shows error message

This is normal if database is not running. The app works without it.

To enable database features, start the database (local or remote).

## Configuration Summary

| Method | Use Case | Setup |
|--------|----------|-------|
| **Local DB** | Development, Testing | `docker-compose up -d` |
| **Remote DB** | Production, Shared Leaderboard | Edit launch script with credentials |
| **No DB** | Offline, Demo | No setup needed |

## More Information

See the comprehensive guide:
```
../DESKTOP_APP_DATABASE_CONFIG.md
```

For database connection code:
```
../geochallenge-backend/db/connection.py
```