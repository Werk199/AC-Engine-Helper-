# AC-Engine-Helper


#  AC Lut Visual Editor

This is a Python script that allows you to interactively edit and visualize Look Up Tables (LUTs).

##  Features

* Load and edit LUT files in the common LUT format (RPM, Torque_NM)
* Visualize the LUT as a scatter plot
* Drag and drop points to interactively modify the LUT curve
* Save changes to the original LUT file or a new file
* Create a backup of the original LUT file before saving changes

##  Getting Started

###  Requirements

* Python 3.x
* matplotlib
* pandas
* tkinter

You can install the required libraries using pip:

```bash
pip install matplotlib pandas tkinter
```

###  Usage

1. Clone or download the repository.
2. Open a terminal in the project directory.
3. Run the script:

```bash
python lut_editor.py
```

4. Select a LUT file to load when prompted.
5. Edit the LUT curve by dragging the data points in the plot.
6. Click the "Save" button to save the changes to the original file.
7. Click the "Save As" button to save the changes to a new file.
8. Click the "Refresh" button to update the plot with any unsaved changes.

##  File Format

The LUT editor supports LUT files in the following format:

```
RPM | Torque_NM
```

Each line of the file represents a data point, with the RPM value separated from the Torque_NM value by a pipe character ("|").

##  Example

```
1000 | 50
2000 | 100
3000 | 150
```

This example LUT file defines three data points for an engine:

* At 1000 RPM, the torque is 50 Nm.
* At 2000 RPM, the torque is 100 Nm.
* At 3000 RPM, the torque is 150 Nm.

You can use the LUT editor to modify these values and visualize the resulting torque curve.

##  License

This software is licensed under the MIT license. See the LICENSE file for more information.
