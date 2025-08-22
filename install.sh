rm -rf build dist
rm -rf *.c *.so
python setup.py build_ext --inplace
mkdir -p dist
mv *.so dist/
pyinstaller beck-view-gui.spec --noconfirm
mv dist/beck-view-gui-bundle/beck-view-gui .
chmod +x ./beck-view-gui
dir=$(pwd -P)
echo 'Executable `beck-view-gui` ready for usage in directory' $dir