# Beck View GUI

The Beck-View GUI App supplies a user-friendly interface to configure the various settings for the [Beck-View-Digitalize](https://github.com/JuPfu/beck-view-digitalize)
Application, such as output directory, camera device number, and other technical attributes. It is built
using `ttkbootstrap` for a modern and consistent look and feel across different operating systems.

![Beck View GUI](./assets/img/beck-view-gui.png)
Beck-View-GUI started without FT232H Chip attached

## Features

- **Device Configuration**: Select the camera device and set the maximum number of frames to digitize.
- **Output Directory**: Choose the directory where the digitized images will be saved.
- **Performance Tuning**: Set the chunk size for parallel processing of images.
- **Real-time Monitoring**: Optionally display a preview window with the digitized images.
- **Subprocess Management**: Start and stop the digitization process with proper handling of subprocess termination for cleanup.

## Requirements

- Python 3.8 or later
- Dependencies listed in `requirements.txt`

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/JuPfu/beck-view-gui.git
    cd beck-view-gui
    ```

2. **Set up a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```sh
    pip install -r requirements.txt
    ```
4. **Optionally Install a standalone application:**

    Windows
    ```sh
    install.bat
    ```
   
    MacOS
    ```sh
    ./install.sh
    ```
   
## Usage

1. **Start the Application**:

    Windows
   - Run `python beck_view_gui.py` to launch the GUI.
   - In case you built a standalone application run `beck-view-gui.exe` 
   
    MacOS
   - Run `python beck_view_gui.py` to launch the GUI.
   - In case you built a standalone application run `./beck-view-gui` 

2. **Configure Settings**:
   - Select the camera device number.
   - Choose the maximum number of frames to digitize.
   - Choose the resolution which is used to digitise images.
   - Set the output directory for digitized images.
   - Adjust the chunk size for parallel image processing.
   - Enable the monitor window if needed.

3. **Start Digitization**:
   - Click the "Start Digitization" button to begin the process.
   - The output from the subprocess will be displayed in real-time in the output text area.

4. **Stop Digitization**:
   - Click the "Stop Digitization" button to terminate the subprocess. The subprocess will handle cleanup before exiting.

## Creating an Executable with Nuitka

To distribute Beck View GUI as a standalone executable, you can use Nuitka, a Python-to-C++ compiler. Below are the steps to set up and create the executable.

### Installing Nuitka

1. **Install Nuitka:**

    ```sh
    pip install nuitka
    ```

2. **Install required C/C++ compilers:**

    Follow the `Nuitka` guidelines for the installation of required C/C++ compilers.

### Creating the Executable

1. **Compile the Python script:**

    Navigate to the project directory where `beck-view_gui.py` is located and run:

   -  Windows
   ```sh
   python -m nuitka  --windows-console-mode=disable --windows-icon-from-ico=beck-view-digitize.png -o "beck-view-gui" beck_view_gui.py
   ```
   -  MacOS

   ```sh
   python3 -m nuitka  --product-name="beck-view-gui" --standalone --macos-app-icon=beck-view-digitize.png --macos-app-mode=gui --onefile --enable-plugin=tk-inter --tcl-library-dir=/opt/homebrew/Cellar/tcl-tk/9.0.1/lib --tk-library-dir=/opt/homebrew/Cellar/tcl-tk/9.0.1/lib --static-libpython=no -o "beck-view-gui" beck_view_gui.py
   ```
   With `Nuitka` version 2.7.11 the build process emits an error message on macOS

    >  FATAL: Error, call to '/usr/bin/codesign' failed: ['/usr/bin/codesign', '-s', '-', '--force', '--deep', '--preserve-metadata=entitlements', 'beck-view-gui'] -> b'beck-view-gui: bundle format unrecognized, invalid, or unsuitable\nIn subcomponent: /Users/jp/PycharmProjects/beck-view-gui/beck_view_gui.onefile-build'.

   Nevetheless a `beck-view-gui` file had been created. After applying `chmod +x` on this file the application seems to work.


2. **Running the Executable:**

    After the compilation is complete, `Nuitka` will give you a notice where to find the executable. You can run it directly:

    - On Windows:

        ```sh
        beck-view-gui.exe
        ```
      or
         ```bat
         python beck_view_gui.py
         ```
       - On Unix or MacOS:

        ```sh
        beck-view-gui
        ```
      or
         ```sh
         python beck_view_gui.py
         ```
      
## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For questions or suggestions, please open an issue on GitHub.

------
This README provides an overview of the project, installation instructions, usage guidelines, and steps to create an executable with Nuitka. Feel free to adjust it according to any additional details specific to your project.