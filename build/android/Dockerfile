# ─────────────────────────────────────────────────────────────────────────────
# GeoChallenge Android APK Builder
#
# Installs:
#   • OpenJDK 17
#   • Android SDK (command-line tools + platform-tools + build-tools 34.0.0)
#   • Android NDK r25c  (required by Panda3D Android cross-compiler)
#   • Python 3.11 + pip
#   • Panda3D + all game dependencies
#   • p3d (Panda3D packaging tool) to produce the APK
# ─────────────────────────────────────────────────────────────────────────────
FROM ubuntu:22.04

# ── Environment ───────────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    ANDROID_HOME=/opt/android-sdk \
    ANDROID_NDK_HOME=/opt/android-sdk/ndk/25.2.9519653 \
    NDK_VERSION=25.2.9519653 \
    BUILD_TOOLS_VERSION=34.0.0 \
    PLATFORM_VERSION=android-33 \
    CMDLINE_TOOLS_VERSION=11076708 \
    PATH="/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:/opt/android-sdk/build-tools/34.0.0:${PATH}"

# ── System dependencies ───────────────────────────────────────────────────────
# NOTE: bump APT_CACHE_DATE to force apt layer rebuild when adding packages
ARG APT_CACHE_DATE=2026-03-15
RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        python3.11 \
        python3.11-venv \
        python3-pip \
        wget \
        unzip \
        curl \
        git \
        libgles2-mesa-dev \
        libx11-dev \
        ca-certificates \
        # python-for-android build dependencies
        autoconf \
        automake \
        libtool \
        pkg-config \
        zlib1g-dev \
        libncurses5-dev \
        libffi-dev \
        libssl-dev \
        libltdl-dev \
        cmake \
        ccache \
        lld \
        patch \
        patchelf \
        tar \
        zip \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
 && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# ── Android SDK command-line tools ────────────────────────────────────────────
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools && \
    wget -q \
        "https://dl.google.com/android/repository/commandlinetools-linux-${CMDLINE_TOOLS_VERSION}_latest.zip" \
        -O /tmp/cmdline-tools.zip && \
    unzip -q /tmp/cmdline-tools.zip -d /tmp/cmdline-tools-tmp && \
    mv /tmp/cmdline-tools-tmp/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest && \
    rm -rf /tmp/cmdline-tools.zip /tmp/cmdline-tools-tmp

# Accept licences non-interactively
RUN yes | sdkmanager --licenses > /dev/null 2>&1 || true

# ── Android SDK components ────────────────────────────────────────────────────
RUN sdkmanager --install \
        "platform-tools" \
        "platforms;${PLATFORM_VERSION}" \
        "build-tools;${BUILD_TOOLS_VERSION}" \
        "ndk;${NDK_VERSION}"

# ── Python virtual environment + game dependencies ────────────────────────────
WORKDIR /app

COPY p3d/requirements.txt /app/requirements.txt

RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install \
        python-for-android \
        panda3d \
        geopandas \
        numpy \
        shapely \
        matplotlib \
        requests

ENV PATH="/app/venv/bin:${PATH}"

# ── Copy source ───────────────────────────────────────────────────────────────
COPY p3d/ /app/p3d/

# ── Build APK ─────────────────────────────────────────────────────────────────
WORKDIR /app/p3d

# build/android/build.sh is copied in and run at container start
COPY build/android/build.sh /app/build.sh
RUN chmod +x /app/build.sh

CMD [ "/app/build.sh" ]

