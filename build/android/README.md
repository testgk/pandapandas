# GeoChallenge Android Build — README
# =====================================

## Overview

`build/android/` contains everything needed to cross-compile GeoChallenge
into an Android APK entirely inside Docker — no local Android SDK or NDK
installation required.

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Ubuntu 22.04 image — installs JDK 17, Android SDK 33, NDK r25c, Python 3.11 + all game deps |
| `docker-compose.yml` | Convenience wrapper — maps the output volume and passes env vars |
| `build.sh` | Build script run inside the container — generates `panda3d_app.pdef` and calls `ppackage` |
| `output/` | Created automatically — the finished APK lands here |

## Quick start

```bash
cd build/android

# 1. Build the Docker image (only needed once / when Dockerfile changes)
docker compose build

# 2. Produce the APK  →  output/geochallenge.apk
docker compose run --rm apk
```

## Environment variables

Override at runtime to customise the build:

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `geochallenge` | APK base name |
| `APP_VERSION` | `1.0` | Version string |
| `APP_PACKAGE` | `com.geochallenge.game` | Android package ID |
| `ANDROID_MODE` | `android` | Launch mode passed to globe_launcher.py |

Example:

```bash
APP_VERSION=2.0 APP_PACKAGE=com.myorg.geochallenge docker compose run --rm apk
```

## Install on device

```bash
# Enable USB debugging on the Android device, then:
adb install output/geochallenge.apk
```

## How it works

1. **Dockerfile** downloads the Android SDK command-line tools, installs
   `platforms;android-33`, `build-tools;34.0.0` and `ndk;25.2.9519653`.
2. **build.sh** generates a `panda3d_app.pdef` descriptor that tells
   Panda3D's `ppackage` tool the entry-point (`globe_launcher`),
   required pip packages, and Android manifest values.
3. `ppackage --platform android_arm64` cross-compiles the Python runtime
   and all assets using the NDK and produces a signed debug APK.
4. The APK is written to `build/android/output/` via a Docker volume mount.

## Requirements

- Docker 20.10+ with BuildKit enabled
- ~8 GB free disk space (NDK + SDK + image layers)
- Internet access during `docker compose build` (downloads SDK/NDK)

