FROM ubuntu:17.04

# Update ubuntu:
RUN set -x \
    && apt-get update -qq \
    && apt-get -y full-upgrade \
    && apt-get autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# install needed packages for buildozer
# https://github.com/kivy/buildozer/blob/master/buildozer/tools/packer/scripts/additional-packages.sh
RUN set -x \
    && dpkg --add-architecture i386 \
    && apt-get update -qq \
    && apt-get -y install \
        lib32stdc++6 lib32z1 lib32ncurses5 \
        build-essential \
        # missing packages:
        python-pip unzip \
    && apt-get -y install git openjdk-8-jdk --no-install-recommends zlib1g-dev \
    && apt-get autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# The buildozer VM used Cython v0.25
RUN set -x \
    && pip install -U pip \
    && pip install "cython<0.26" \
    && pip install buildozer python-for-android pyOpenssl

ADD kivy_hello_world /buildozer/kivy_hello_world

RUN set -x \
    && adduser buildozer --disabled-password --disabled-login \
    && chown -R buildozer:buildozer /buildozer/

USER buildozer

# download all needed andorid dependencies:
RUN set -x \
    && cd /buildozer/kivy_hello_world \
    && buildozer android debug update \
    && cd .. \
    && rm -rf kivy_hello_world

VOLUME /buildozer/

WORKDIR /buildozer/
