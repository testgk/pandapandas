#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# test.sh  —  Test the GeoChallenge Android APK
#
# Usage:
#   ./test.sh                  # auto-detect: real device > emulator > static
#   ./test.sh --static         # static APK validation only (no device needed)
#   ./test.sh --device         # real USB device only
#   ./test.sh --emulator       # start emulator and install
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OUTPUT_DIR="${SCRIPT_DIR}/output"
APP_PACKAGE="${APP_PACKAGE:-com.geochallenge.game}"
APP_VERSION="${APP_VERSION:-1.0}"
APP_NAME="${APP_NAME:-geochallenge}"
APK_PATH="${OUTPUT_DIR}/${APP_NAME}-${APP_VERSION}.apk"
ANDROID_HOME="${ANDROID_HOME:-${HOME}/Android/Sdk}"
AVD_NAME="geochallenge_test"
MODE="${1:---auto}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log()    { echo -e "${GREEN}[TEST]${NC} $*"; }
warn()   { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()   { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

# ── Check APK exists ──────────────────────────────────────────────────────────
if [ ! -f "${APK_PATH}" ]; then
    # Try any APK in output/
    APK_PATH=$( find "${OUTPUT_DIR}" -name "*.apk" 2>/dev/null | head -1 || true )
    if [ -z "${APK_PATH}" ]; then
        fail "No APK found in ${OUTPUT_DIR}/\n  Run:  docker compose run --rm apk"
    fi
fi
log "APK: ${APK_PATH}  ($( du -sh "${APK_PATH}" | cut -f1 ))"

# ── Static validation (always runs) ──────────────────────────────────────────
static_test() {
    log "Running static APK validation ..."

    # Use aapt/apksigner from the Docker image if not available locally
    if command -v aapt &>/dev/null && command -v apksigner &>/dev/null; then
        log "  Using local build-tools ..."
        aapt dump badging "${APK_PATH}" | grep -E "package|activity|sdkVersion|targetSdkVersion"
        apksigner verify --verbose "${APK_PATH}" && log "  ✅ APK signature valid" || warn "  APK unsigned (debug build — OK for testing)"
    else
        log "  Using Docker build-tools ..."
        docker run --rm \
            -v "${OUTPUT_DIR}:/apk:ro" \
            android-apk:latest \
            bash -c "
                APK=\$(ls /apk/*.apk | head -1)
                echo '--- Package metadata ---'
                \${ANDROID_HOME}/build-tools/34.0.0/aapt dump badging \"\${APK}\" \
                    | grep -E 'package|activity|sdkVersion|targetSdkVersion|native-code' || true
                echo ''
                echo '--- Signature check ---'
                \${ANDROID_HOME}/build-tools/34.0.0/apksigner verify --verbose \"\${APK}\" 2>&1 \
                    || echo 'Unsigned debug APK (expected for dev builds)'
                echo ''
                echo '--- APK contents (top level) ---'
                unzip -l \"\${APK}\" | grep -v '/$' | awk '{print \$NF}' \
                    | grep -v '__MACOSX' | head -40 || true
            " 2>&1
        log "  ✅ Static validation complete"
    fi
}

# ── Install on real device ────────────────────────────────────────────────────
device_test() {
    log "Looking for connected Android device ..."
    if ! command -v adb &>/dev/null; then
        # Try to find adb from ANDROID_HOME
        ADB="${ANDROID_HOME}/platform-tools/adb"
        [ -x "${ADB}" ] || fail "adb not found. Install Android platform-tools or set ANDROID_HOME."
    else
        ADB="adb"
    fi

    DEVICE=$( "${ADB}" devices | grep -v "List" | grep "device$" | awk '{print $1}' | head -1 )
    if [ -z "${DEVICE}" ]; then
        warn "No device connected."
        return 1
    fi

    log "  Device: ${DEVICE}"
    log "  Installing APK ..."
    "${ADB}" -s "${DEVICE}" install -r "${APK_PATH}"
    log "  Launching app ..."
    "${ADB}" -s "${DEVICE}" shell am start -n "${APP_PACKAGE}/.PythonActivity" 2>/dev/null \
        || "${ADB}" -s "${DEVICE}" shell monkey -p "${APP_PACKAGE}" -c android.intent.category.LAUNCHER 1
    log "  ✅ Installed and launched on ${DEVICE}"
    log ""
    log "  Watching logs  (Ctrl+C to stop):"
    log "    adb -s ${DEVICE} logcat -s python:V SDL:V"
    log ""
    read -p "  Watch logs now? [y/N] " -n 1 -r; echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        "${ADB}" -s "${DEVICE}" logcat -s python:V SDL:V ActivityManager:I
    fi
    return 0
}

# ── Emulator test ─────────────────────────────────────────────────────────────
emulator_test() {
    log "Setting up Android emulator ..."
    ADB="${ANDROID_HOME}/platform-tools/adb"
    EMULATOR="${ANDROID_HOME}/emulator/emulator"
    SDKMANAGER="${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager"
    AVDMANAGER="${ANDROID_HOME}/cmdline-tools/latest/bin/avdmanager"

    for BIN in "${ADB}" "${EMULATOR}" "${SDKMANAGER}" "${AVDMANAGER}"; do
        [ -x "${BIN}" ] || fail "Not found: ${BIN}\n  Install Android Studio or set ANDROID_HOME correctly."
    done

    # Install system image if needed
    SI="system-images;android-33;google_apis;x86_64"
    if ! "${SDKMANAGER}" --list_installed 2>/dev/null | grep -q "${SI}"; then
        log "  Installing system image: ${SI} ..."
        echo "y" | "${SDKMANAGER}" "${SI}"
    fi

    # Create AVD if needed
    if ! "${AVDMANAGER}" list avd 2>/dev/null | grep -q "${AVD_NAME}"; then
        log "  Creating AVD: ${AVD_NAME} ..."
        echo "no" | "${AVDMANAGER}" create avd \
            -n "${AVD_NAME}" \
            -k "${SI}" \
            --device "pixel_6" \
            --force
    fi

    log "  Starting emulator (this takes ~30s) ..."
    "${EMULATOR}" -avd "${AVD_NAME}" -no-audio -no-window &
    EMULATOR_PID=$!

    log "  Waiting for device boot ..."
    "${ADB}" wait-for-device
    # Wait for full boot
    until "${ADB}" shell getprop sys.boot_completed 2>/dev/null | grep -q "1"; do
        sleep 3
    done
    log "  Emulator booted."

    log "  Installing APK ..."
    "${ADB}" install -r "${APK_PATH}"
    log "  Launching app ..."
    "${ADB}" shell am start -n "${APP_PACKAGE}/.PythonActivity"

    log "  ✅ Running in emulator (PID: ${EMULATOR_PID})"
    log "  Watching logs (Ctrl+C to stop):"
    "${ADB}" logcat -s python:V SDL:V ActivityManager:I
}

# ── Main ──────────────────────────────────────────────────────────────────────
static_test

case "${MODE}" in
    --static)
        log "Static-only mode — done."
        ;;
    --device)
        device_test || fail "No device found or install failed."
        ;;
    --emulator)
        emulator_test
        ;;
    --auto|*)
        log "Auto-detecting test target ..."
        # Try real device first, then emulator, then static only
        if device_test 2>/dev/null; then
            log "✅ Tested on real device."
        else
            warn "No device found — emulator test requires local Android Studio."
            warn "Static validation passed. To test on a device:"
            warn "  1. Enable USB Debugging on your Android phone"
            warn "  2. Plug in via USB"
            warn "  3. Run:  ./test.sh --device"
            warn ""
            warn "  Or install directly:"
            warn "  adb install ${APK_PATH}"
        fi
        ;;
esac

