#!/usr/bin/env bash

set -x

pip freeze > packages_vm.txt
dpkg --get-selections | awk '$2 == "install" {print $1}' >> packages_vm.txt