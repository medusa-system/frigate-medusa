#!/bin/bash
set -euo pipefail

# Install system packages required by Python dependencies
sudo apt-get update
sudo apt-get install -y build-essential ffmpeg pkg-config \
    libglib2.0-0 libsm6 libxext6 libxrender1

# Upgrade pip and install Python dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r docker/main/requirements.txt
python3 -m pip install -r docker/main/requirements-wheels.txt
python3 -m pip install -r docker/main/requirements-ov.txt
python3 -m pip install -r docker/main/requirements-dev.txt

# Generate version file
make version

# Run formatting, linting, typing checks, and tests
ruff format frigate docs docker
ruff check frigate docs docker
python3 -m mypy --config-file frigate/mypy.ini frigate
python3 -m unittest
