#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build.sh  —  Build the GeoChallenge Android APK inside Docker
#              Uses python-for-android (p4a) to cross-compile Python + deps
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

APP_NAME="${APP_NAME:-geochallenge}"
APP_VERSION="${APP_VERSION:-1.0}"
APP_PACKAGE="${APP_PACKAGE:-com.geochallenge.game}"
OUTPUT_DIR="/app/output"
P3D_DIR="/app/p3d"
P4A_DIR="/opt/p4a"
BUILD_DIR="/tmp/p4a-build"

echo "============================================================"
echo "  GeoChallenge Android APK Builder"
echo "  App     : ${APP_NAME} v${APP_VERSION}"
echo "  Package : ${APP_PACKAGE}"
echo "============================================================"

# ── [1/6] Verify environment ──────────────────────────────────────────────────
echo "[1/6] Verifying SDK / NDK / Java ..."
java -version 2>&1 | head -1
echo "  ANDROID_HOME     = ${ANDROID_HOME}"
echo "  ANDROID_NDK_HOME = ${ANDROID_NDK_HOME}"
echo "  JAVA_HOME        = ${JAVA_HOME}"

# ── [2/6] Install python-for-android ─────────────────────────────────────────
echo "[2/6] Installing python-for-android ..."
/app/venv/bin/pip install --quiet python-for-android

# ── [3/6] Prepare output & build dirs ─────────────────────────────────────────
echo "[3/6] Preparing build directories ..."
mkdir -p "${OUTPUT_DIR}" "${BUILD_DIR}"

# ── [4/6] Copy app source ─────────────────────────────────────────────────────
echo "[4/6] Copying app source ..."
cp -r "${P3D_DIR}/"* "${BUILD_DIR}/"

# Ensure a minimal AndroidManifest-compatible main.py entry point exists
# p4a requires a main.py or __main__.py at the root
if [ ! -f "${BUILD_DIR}/main.py" ]; then
    cat > "${BUILD_DIR}/main.py" << 'MAINPY'
import sys
import os
sys.path.insert( 0, os.path.dirname( __file__ ) )
from globe_launcher import launch
from app_mode import AppMode
launch( AppMode.ANDROID )
MAINPY
fi

# ── [5/6] Build APK with p4a ──────────────────────────────────────────────────
echo "[5/6] Building APK with python-for-android ..."

cd "${BUILD_DIR}"

/app/venv/bin/python3 -m pythonforandroid.toolchain apk \
    --private        "${BUILD_DIR}" \
    --package        "${APP_PACKAGE}" \
    --name           "${APP_NAME}" \
    --version        "${APP_VERSION}" \
    --android-api    33 \
    --ndk-version    25.2.9519653 \
    --sdk-dir        "${ANDROID_HOME}" \
    --ndk-dir        "${ANDROID_NDK_HOME}" \
    --arch           arm64-v8a \
    --requirements   python3,requests,numpy \
    --bootstrap      sdl2 \
    --release \
    --debug \
    --dist-name      "${APP_NAME}" \
    2>&1 | tee /tmp/p4a_build.log

# ── [6/6] Locate and report APK ───────────────────────────────────────────────
echo "[6/6] Looking for APK ..."

# p4a puts the APK in the current directory by default
APK_PATH=$( find "${BUILD_DIR}" /tmp /root -name "*.apk" 2>/dev/null | head -1 || true )

if [ -z "${APK_PATH}" ]; then
    # Also check p4a default dist output
    APK_PATH=$( find ~/.local /root -name "*.apk" 2>/dev/null | head -1 || true )
fi

if [ -n "${APK_PATH}" ]; then
    cp "${APK_PATH}" "${OUTPUT_DIR}/${APP_NAME}-${APP_VERSION}.apk"
    APK_SIZE=$( du -sh "${OUTPUT_DIR}/${APP_NAME}-${APP_VERSION}.apk" | cut -f1 )
    echo ""
    echo "  ✅  APK ready: ${OUTPUT_DIR}/${APP_NAME}-${APP_VERSION}.apk  (${APK_SIZE})"
    echo ""
    echo "  Install on device:"
    echo "    adb install ${OUTPUT_DIR}/${APP_NAME}-${APP_VERSION}.apk"
else
    echo ""
    echo "  ⚠️  APK not found — build output:"
    tail -40 /tmp/p4a_build.log
    ls -la "${BUILD_DIR}" || true
    exit 1
fi

echo "============================================================"

