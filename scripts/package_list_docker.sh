#!/usr/bin/env bash

set -x

docker run buildozer pip freeze > packages_docker.txt
docker run buildozer dpkg --get-selections | awk '$2 == "install" {print $1}' >> packages_docker.txt
