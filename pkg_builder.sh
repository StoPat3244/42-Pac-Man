#!/bin/sh

python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --onedir \
    --name "42-Pac-Man" \
    --add-data "assets:assets" \
    --add-data "config.json:." \
    pac-man.py