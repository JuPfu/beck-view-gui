# Beck-View GUI

## Overview

The Beck-View GUI App supplies a user-friendly interface to configure the various settings for the [Beck-View-Digitalize](https://github.com/JuPfu/beck-view-digitalize)
Application, such as output directory, camera device number, and other technical attributes. It is built
using `ttkbootstrap` for a modern and consistent look and feel across different operating systems.

## Features

- **Output Directory Selection:** Choose the directory where digitized images will be stored.
- **Technical Attributes Configuration:** Set the maximum number of images and the number of parallel images to process.
- **Preferences Setup:** Configure the camera device number and toggle the display of a monitor window showing digitized
  images.
- **Menu Options:** Access file and window management options from the menu bar.
- **Splash Screen:** Display a splash screen upon startup.
- **Start Digitization:** Launch the digitization process with the configured settings.

## Requirements

- Python 3.x
- `ttkbootstrap` library
- `tkinter` library (usually comes pre-installed with Python)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/JuPfu/beck-view-gui.git
   cd beck-view-gui
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```bash
   python main.py
   ```

## Usage

### Main Components

#### FrameOutputDirectory

This frame allows users to select the directory where digitized images will be stored.

#### TechnicalAttributes

This frame provides options to set the maximum number of images and the batch size for parallel processing.

#### Preferences

This frame includes settings for the camera device number and a checkbox to enable or disable the monitor window.

#### MainMenu

This class creates the main menu with options for file and window management.

### How to Use

1. **Launch the Application:**
   Run the application using the command mentioned in the installation section.

2. **Configure Settings:**
    - **Output Directory:** Click on the "Auswählen" button to open a dialog for selecting the output directory.
    - **Technical Attributes:** Choose the maximum number of images and the batch size from the dropdown and spinbox
      respectively.
    - **Preferences:** Set the camera device number and enable/disable the monitor window using the provided spinbox and
      checkbox.

3. **Start Digitization:**
   Click on the "Start Digitalisierung" button to begin the digitization process. The application will launch a
   subprocess to handle the digitization with the configured settings.

## File Structure

```
beck-view/
│
├── main.py                 # Main application script
├── README.md               # This README file
├── beck-view-digitize.png  # Splash screen image
└── requirements.txt        # Python dependencies
```

## Contributing

1. **Fork the Repository**
2. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/your-feature
   ```
3. **Commit Changes:**
   ```bash
   git commit -m 'Add some feature'
   ```
4. **Push to the Branch:**
   ```bash
   git push origin feature/your-feature
   ```
5. **Open a Pull Request**

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) for providing a modern and customizable theme
  for `tkinter`.

---

Feel free to explore and customize the Beck-View-GUI App to suit your specific needs. Happy digitizing!
