#!/usr/bin/env bash
set -e

rm -rf build dist
rm -f *.c *.so

python -m pip install --upgrade pip setuptools wheel cython pyinstaller

# Compile Cython extensions
python setup.py build_ext --inplace

# Move compiled extensions into dist
mkdir -p dist
mv *.so dist/

# Build executable
pyinstaller beck-view-gui.spec --noconfirm

# Move executable to project root
mv dist/beck-view-gui-bundle/beck-view-gui .
chmod +x ./beck-view-gui

echo "Executable beck-view-gui ready in $(pwd -P)"