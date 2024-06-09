# Beck View GUI

The Beck-View GUI App supplies a user-friendly interface to configure the various settings for the [Beck-View-Digitalize](https://github.com/JuPfu/beck-view-digitalize)
Application, such as output directory, camera device number, and other technical attributes. It is built
using `ttkbootstrap` for a modern and consistent look and feel across different operating systems.
## Features

- **Device Configuration**: Select the camera device and set the maximum number of frames to digitize.
- **Output Directory**: Choose the directory where the digitized images will be saved.
- **Performance Tuning**: Set the chunk size for parallel processing of images.
- **Real-time Monitoring**: Optionally display a preview window with the digitized images.
- **Subprocess Management**: Start and stop the digitization process with proper handling of subprocess termination for cleanup.

## Prerequisites

- Python 3.7 or higher
- `ttkbootstrap` library
- `asyncio` library (comes with Python 3.7+)

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/JuPfu/beck-view-gui.git
   cd beck-view-gui
   ```

2. **Install dependencies**:
   ```sh
   pip install ttkbootstrap
   ```

## Running the Application

To start the GUI application, run the following command:

```sh
python beck_view_gui.py
```

## Usage

1. **Start the Application**:
   - Run `python beck_view_gui.py` to launch the GUI.

2. **Configure Settings**:
   - Select the camera device number.
   - Choose the maximum number of frames to digitize.
   - Set the output directory for digitized images.
   - Adjust the chunk size for parallel image processing.
   - Enable the monitor window if needed.

3. **Start Digitization**:
   - Click the "Start Digitization" button to begin the process.
   - The output from the subprocess will be displayed in real-time in the output text area.

4. **Stop Digitization**:
   - Click the "Stop Digitization" button to terminate the subprocess. The subprocess will handle cleanup before exiting.


## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For questions or suggestions, please open an issue on GitHub.

```
