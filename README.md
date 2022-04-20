# Introduction
This software was designed to read data from a Measurement Computing Company (MCC) board, as well as use it to control a number of pumps. Analog input channels on the board are used to read thermocouples and conductivity probes. Analog output channels (VDAC) are used to control the pumps.

The core software behind this application was designed to be reusable. For more information [Click Here](#Code-Summary).

# Usage

## Startup
The software can be run using either a Python interpreter running the `controller.pyw` file, by running the `.bat` file in the project directory, or by creating a shortcut to the `.bat` and opening that.

## Changing Pump Flowrates
Pump flowrates can be changed by going to **Pump Control > Pump Flowrates**. 

## Recording Data
To record data, go to **Record Data > Start Data Recording**. This will begin saving the data from all thermocouples, conductivity probes, and pumps. To end data recording, go to **Record Data > Stop Data Recording**. This will end data acquisition and create a `.xlsx` data file in the desired directory.

## Viewing Data & Changing Output Settings
The directory the data file is saved to can be open by going to **File > Open Data Path**.

To change the filename or directory to save the data to, go to **File > Configure Data Path**. 

# Configuring Channels
## Reading Thermocouples 
The Application is currently configured to read a number of channels designated as thermocouples. The list that defines what channels are read is called `self.thermocouple_channels` and is found in the `App` class in the `__init__()` method. The integers in this list correspond to what channels will be read, plotted, and saved.

## Reading Conductivity Probes
The Application is also currently configured to read a number of channels as the output of a conductivity probe. The list that defines what channels are read is called `self.conductivity_channels` and is found in the `App` class in the `__init__()` method. The integers in this list correspond to what channels will be read, plotted, and saved.

## Controlling Pumps
Pumps can be controlled by adding their VDAC channel to the `self.pump_VDAC_channels` list found in the `App` class in the `__init__()` method. Any integers in this list will automatically have a dialog created to control them in the **Pump Control** menu. 

For every VDAC channel added to this list, a set of calibration values must be added to convert the desired flowrate to a voltage. These calibration values were collected by plotting the voltage (V) inputted into the pump against the measured flow rate(mL/min). A linear equation can be obtained from this plot to act as a calibration curve. For more information on the calibration curve [Click Here](https://github.com/EthanThePorter/MCC-DAQ/blob/master/calibrations/Pump%20Calibration.xlsx). 

For example, if you wanted to control a pump connected to **VDAC Channel 2** with a calibration curve slope of **0.049** and a y-intercept of **2.41**:

```python
self.pump_VDAC_channels = [2]
self.pump_calibration = {2: (0.049, 2.41)}
```

To add another pump connected to **VDAC Channel 3** with a calibration curve slope of **0.056** and a y-intercept of **3.51** the previous code would become:

```python
self.pump_VDAC_channels = [2, 3]
self.pump_calibration = {2: (0.049, 2.41), 3: (0.056, 3.51)}
```

# Code Summary
The code for this application was designed to be reusable. The `Controller`, `Plot`, and `DataHandler` classes are all standalone and can be used separately. The `App` class contains most the application-specific code. The following code represents the core components of the `App` class that could be used to build a new application. 

* Application initialization code can be entered into the `__init__()` method.
* Application runtime code can be entered into the `main_update()` method.
* Application exit code can be entered into the `on_closing()` method.

The `main_thread()` method should not be changed as it regulates the app to run `main_update()` at the interval specified by the `refresh_time` variable with an accuracy of ± 3ms.

More information on creating a `.bat` file to run the main Python file of your code can be found [Here](https://github.com/EthanThePorter/MCC-DAQ/blob/master/README.txt).

```python
from tkinter import *
import numpy as np
import time


class App(Tk):


    def __init__(self, refresh_time: int, *args, **kwargs):
        """
        Main Application class.

        :param refresh_time: Time in ms for refresh. Use whole numbers (i.e. 1000, 2000, 5000, etc).
        """
        Tk.__init__(self, *args, **kwargs)

        # Initializes refresh rate to update main thread
        self.refresh_time = refresh_time

        # Initializes application start time
        self.start_time = time.time()
        self.start_time_adjusted = False

        # Initializes variable to account for time lost to rounding when regulating app runtime
        self.rounding_time_loss = 0

        # Initializes runtime array to track each time when main_thread() is executed. Used for data collection and timing.
        self.runtime = []


        # Enter initialization code here.


    def on_closing(self):
        """
        Method that handles the application being closed. 
        """

        # Enter code to run on application close here.

        # Closes application
        self.destroy()


    def main_thread(self):
        """
        Function that regulates app to ensure consistent refresh time
        """

        # Gets start time of main_thread() for making data readout consistent
        update_runtime_start = time.time()

        # Adjust data start time to ensure data starts at 0.0s. Only runs first time main_thread() is run
        if not self.start_time_adjusted:
            self.start_time += time.time() - self.start_time
            self.start_time_adjusted = True

        #Gets time and rounds - adds to runtime array - data will be collected at self.refresh_rate
        relative_time = np.round(time.time() - self.start_time, 1)
        self.runtime.append(relative_time)

        print(time.time() - self.start_time)

        # Initializes value for time drift correction
        offset_time = (time.time() - self.start_time) * 1000
        offset_time_int = round(offset_time, -2)
        delta_time = int(offset_time - offset_time_int)


        # Starts timer to monitor main_update() runtime
        runtime = time.time()

        # Main update function where runtime code goes
        self.main_update()

        # Ends timer to monitor main_update() runtime and converts to (ms)
        runtime = int((time.time() - runtime) * 1000)

        # If runtime of main_update() excess refresh time, output error to terminal
        if runtime > self.refresh_time:
            print("\n\033[0;31mWARNING: Runtime of main thread exceeded refresh rate.\nRefresh rate: "
                  + str(self.refresh_time) + " ms \nRuntime: " + str(round(runtime, 1)) + " ms\n\033[0;30m")


        # Gets time taken to run function and outputs to console
        update_runtime_finish = (time.time() - update_runtime_start) * 1000
        # print(update_runtime_finish)

        # Gets time in ms to reduce time till refresh, accounting for time took to run code
        adjusted_time = self.refresh_time - update_runtime_finish
        adjusted_time_floored = int(round(adjusted_time, 0))

        # Applies time offset
        if delta_time > 1:
            adjusted_time_floored -= delta_time

        # End of function command to repeat,
        self.after(adjusted_time_floored, self.main_thread)


    def main_update(self):
        """
        Main runtime method that contains all code to execute during app runtime.
        """

        # Enter code to run during application runtime here.


# Runs app and updates every 1000ms.
# App will output error to terminal if operation time exceeds refresh rate.
app = App(1000)
# Sets handler for application closing event
app.protocol("WM_DELETE_WINDOW", app.on_closing)
# Runs main app thread during runtime
app.main_thread()
app.mainloop()
```











