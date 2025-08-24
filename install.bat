rmdir /S /Q build
rmdir /S /Q dist
del *.c *.pyd
python setup.py build_ext --inplace
mkdir dist
move *.pyd dist
pyinstaller beck-view-gui.spec --noconfirm
copy /y dist\beck-view-gui-bundle\beck-view-gui.exe "%CD%"
echo "Executable `beck-view-gui.exe` ready for usage in directory %CD%"