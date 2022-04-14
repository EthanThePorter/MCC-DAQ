# Used by Controller
from __future__ import absolute_import, division, print_function
from builtins import *
from mcculw import ul
from mcculw.enums import ULRange, InfoType, BoardInfo, AiChanType, AnalogInputMode, TcType, TempScale, TInOptions

# Used by all classes
import numpy as np

# Used by Plot & App
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# Used by Plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style

# Used by App
import time

# Used by DataHandler
import pandas as pd
import sys
import os
import xlsxwriter
import subprocess


class App(Tk):

    def __init__(self, refresh_time, *args, **kwargs):
        """
        Main App class

        :param refresh_time: Time in ms for refresh
        """
        Tk.__init__(self, *args, **kwargs)

        # Initializes time to update main thread
        self.refresh_time = refresh_time

        # Initializes start time
        self.start_time = time.time()
        self.start_time_adjusted = False

        # Initializes variable to account for time lost to rounding
        self.rounding_time_loss = 0


        # Window settings
        self.title('MCC-DAQ')
        self.config(padx=10, pady=10)
        self.config(background='white')
        self.iconbitmap('assets/uwicon.ico')
        self.geometry('+100+100')


        # Create menu bar
        menubar = Menu(self)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Data Path", command=self.open_data_window)
        menubar.add_cascade(label="File", menu=filemenu)

        datamenu = Menu(menubar, tearoff=0)
        datamenu.add_command(label="Start Data Recording", command=self.start_recording)
        datamenu.add_command(label="Stop Data Recording", command=self.end_recording)
        menubar.add_cascade(label="Record Data", menu=datamenu)

        # Add to main frame
        self.config(menu=menubar)


        # Thermocouple channels to read
        self.thermocouple_channels = [0, 1, 8, 11]

        # Conductivity channels to read
        self.conductivity_channels = [2, 3]

        # Configure channels to read thermocouples
        Controller.initialize_thermocouple_read(self.thermocouple_channels)

        # Configure channels to read voltage from conductivity channels
        Controller.initialize_analog_read(self.conductivity_channels)

        # Initializes empty lists for temperature, conductivity, and time to be saved to
        self.temperature = [[] for _ in self.thermocouple_channels]
        self.conductivity = [[] for _ in self.conductivity_channels]
        self.runtime = []

        # Create main frame for holding plots
        self.main_plot_frame = Frame(self)
        self.main_plot_frame.pack()

        # Create thermocouple plot
        self.plot_frame = Frame(self.main_plot_frame)
        self.plot_frame.pack(side=LEFT)
        self.plot = Plot(self.plot_frame, "Channel Temperature Data", "Time (s)", "Temperature (°C)", figure_size=(4, 6))

        # Create conductivity plot
        self.conductivity_plot_frame = Frame(self.main_plot_frame)
        self.conductivity_plot_frame.pack(side=RIGHT)
        self.conductivity_plot = Plot(self.conductivity_plot_frame, "Channel Conductivity Data", "Time (s)", "Conductivity (mS)", figure_size=(4, 6))


        # Create recording label on bottom
        self.recording_label = Label(self, text="", background='white')
        self.recording_label.pack(side=LEFT, pady=5)

        # Initialize variables for recording
        self.recording_in_progress = False
        self.recording_time_start = 0


        # Initialize path and filename for data saving
        self.data_path = "C:/Users/labuser/Desktop/MCC-DAQ"
        self.filename = "MCC-DAQ Data"


    def open_data_window(self):

        # Create a Toplevel window
        data_window = Toplevel(self, background='white')
        data_window.iconbitmap('assets/uwicon.ico')
        data_window.resizable(False, False)

        # Label for data processing
        Info_label = Label(data_window, text='Ensure Path & Filename does\nnot contain special characters', background='white')
        Info_label.pack(pady=(10, 20))

        # Label for data path
        Path_label = Label(data_window, text='Data Directory Path', background='white')
        Path_label.pack(padx=10, pady=(10, 2))

        # Entry for data path
        data_path_entry = Entry(data_window, width=40)
        data_path_entry.insert(END, self.data_path)
        data_path_entry.pack(padx=10, pady=(0, 10))

        # Label for filename
        filename_label = Label(data_window, text='Filename', background='white')
        filename_label.pack(padx=10, pady=(10, 2))

        # Entry for filename
        filename_entry = Entry(data_window, width=40)
        filename_entry.insert(END, self.filename)
        filename_entry.pack(padx=10, pady=(0, 10))

        # Button for applying changes
        apply_button = Button(data_window, text='Apply', command=lambda: self.close_data_window(data_window,
                                                                                                data_path_entry.get(),
                                                                                                filename_entry.get()))
        apply_button.config(width=20)
        apply_button.pack(padx=10, pady=10)


    def close_data_window(self, window, path, filename):

        # Cleans path and filename
        cleaned_path = path.strip()
        cleaned_filename = filename.strip()

        # Updates filename and path
        self.data_path = cleaned_path
        self.filename = cleaned_filename

        # Closes popup
        window.destroy()


    def start_recording(self):
        """
        Method to initiate App data recording.
        """

        # If recording isn't already in progress
        if not self.recording_in_progress:

            # Mark that recording is in progress
            self.recording_in_progress = True

            # Get recording time start
            self.recording_time_start = self.runtime[-1]

            # Updates recording label
            self.recording_label.config(text="Recording Started at: " + str(int(self.recording_time_start)) + "s")


    def end_recording(self):
        """
        Method to stop App data recording
        """

        #Checks if recording is in progress
        if self.recording_in_progress:

            # Set recording to false
            self.recording_in_progress = False

        # Configure label
        self.recording_label.config(text='Recording Stopped at: ' + str(int(self.runtime[-1])) + "s")


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
        # Gets temperatures
        current_temperatures_not_rounded = Controller.thermocouple_instantaneous_read(self.thermocouple_channels)

        # Rounds temperatures
        current_temperatures = np.round(current_temperatures_not_rounded, 1)


        # Gets voltage from conductivity channels
        current_conductivity_V = Controller.analog_read(self.conductivity_channels)

        # Converts voltages to mA with the basis of a 220 Ohm resistor
        current_conductivity_mA = [x / 220 * 1000 for x in current_conductivity_V]

        # Uses calibration equation to convert mA to mS and rounds to 1 decimal place
        current_conductivity_mS = [round(12.64168 * x - 49.99568, 1) for x in current_conductivity_mA]


        # Appends temperature data to main array
        for x in range(len(self.thermocouple_channels)):
            # Appends current temperatures to a 2D list
            self.temperature[x].append(current_temperatures[x])

        # Appends conductivity data to main array
        for x in range(len(self.conductivity_channels)):
            # Appends current temperatures to a 2D list
            self.conductivity[x].append(current_conductivity_mS[x])


        # Formats thermocouple data for plotting - format is a tuple as follows: (x, y, label)
        data = []
        for x in range(len(self.thermocouple_channels)):
            data.append((self.runtime,
                         self.temperature[x],
                         "Channel " + str(self.thermocouple_channels[x]) + ": " + str(current_temperatures[x]) + "°C"))

        # Formats thermocouple data for plotting - format is a tuple as follows: (x, y, label)
        conductivity_data = []
        for x in range(len(self.conductivity_channels)):
            conductivity_data.append((self.runtime,
                         self.conductivity[x],
                         "Channel " + str(self.conductivity_channels[x]) + ": " + str(current_conductivity_mS[x]) + "mS"))

        # Updates plots
        self.plot.update_data(data)
        self.conductivity_plot.update_data(conductivity_data)


        # If data recording is enabled
        if self.recording_in_progress:

            # Gets runtime
            data_offset = int(self.recording_time_start)

            # Initializes DataFrame
            df = pd.DataFrame()

            # Writes runtime to df DataFrame
            df['Runtime (s)'] = [x - data_offset for x in self.runtime[data_offset:]]

            # Writes thermocouple data to df DataFrame
            for x in range(len(self.thermocouple_channels)):
                df['Channel ' + str(self.thermocouple_channels[x]) + ' (°C)'] = self.temperature[x][data_offset:]

            # Writes conductivity data to df Dataframe
            for x in range(len(self.conductivity_channels)):
                df['Channel ' + str(self.conductivity_channels[x]) + ' (mS)'] = self.conductivity[x][data_offset:]

            # Outputs DataFrame to Excel file
            DataHandler.export(df, self.data_path, self.filename)


class Controller:
    """
    Set of functions to interact with MCC control board.
    """
    @staticmethod
    def initialize_thermocouple_read(channel: int | list[int], board_num=0, rate=60, thermocouple_type=TcType.K):

        # If channel is single value setup single channel
        if type(channel) is int:
            # Set channel type to TC (thermocouple)
            ul.set_config(
                InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE,
                AiChanType.TC)
            # Set thermocouple type to type K
            ul.set_config(
                InfoType.BOARDINFO, board_num, channel, BoardInfo.CHANTCTYPE,
                thermocouple_type)
            # Set the temperature scale to Celsius
            ul.set_config(
                InfoType.BOARDINFO, board_num, channel, BoardInfo.TEMPSCALE,
                TempScale.CELSIUS)
            # Set data rate
            ul.set_config(
                InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE, rate)

        # If channel is list setup every channel in list
        if type(channel) is list:
            for i in channel:
                # Set channel type to TC (thermocouple)
                ul.set_config(
                    InfoType.BOARDINFO, board_num, i, BoardInfo.ADCHANTYPE,
                    AiChanType.TC)
                # Set thermocouple type to type K
                ul.set_config(
                    InfoType.BOARDINFO, board_num, i, BoardInfo.CHANTCTYPE,
                    thermocouple_type)
                # Set the temperature scale to Celsius
                ul.set_config(
                    InfoType.BOARDINFO, board_num, i, BoardInfo.TEMPSCALE,
                    TempScale.CELSIUS)
                # Set data rate
                ul.set_config(
                    InfoType.BOARDINFO, board_num, i, BoardInfo.ADDATARATE, rate)

    @staticmethod
    def thermocouple_instantaneous_read(channel: int | list[int], board_num=0):
        """
        Reads thermocouple.

        :param board_num: Board number
        :param channel: Desired channel to read
        :return: Temperature in celsius
        """
        # Configure options for thermocouple read
        options = TInOptions.NOFILTER

        # If channel is single value read and return single channel
        if type(channel) is int:
            return ul.t_in(board_num, channel, TempScale.CELSIUS, options)

        # If channel is list read and return list for every channel in list
        if type(channel) is list:
            return [ul.t_in(board_num, x, TempScale.CELSIUS, options) for x in channel]

    @staticmethod
    def initialize_analog_read(channel: int | list, board_number=0, rate=60):
        """
        Initializes channels to read by analog
        :param channel: Channel or list of channels to be initialized
        :param board_number: Number of board
        :param rate: Rate in hertz at which channel is read.
        """

        # If channel is a single channel
        if type(channel) is int:
            # configure the channel for voltage
            ul.set_config(InfoType.BOARDINFO, board_number, channel, BoardInfo.ADCHANTYPE, AiChanType.VOLTAGE)

            # Set channel to differential mode
            ul.a_chan_input_mode(board_number, channel, AnalogInputMode.DIFFERENTIAL)

            # Set channel rate
            ul.set_config(InfoType.BOARDINFO, board_number, channel, BoardInfo.ADDATARATE, rate)

        # If channel is a list of channels
        if type(channel) is list:

            for x in channel:
                # configure the channel for voltage
                ul.set_config(InfoType.BOARDINFO, board_number, x, BoardInfo.ADCHANTYPE, AiChanType.VOLTAGE)

                # Set channel to differential mode
                ul.a_chan_input_mode(board_number, x, AnalogInputMode.DIFFERENTIAL)

                # Set channel rate
                ul.set_config(InfoType.BOARDINFO, board_number, x, BoardInfo.ADDATARATE, rate)

    @staticmethod
    def analog_read(channel: int | list, board_number=0):
        """
        Function to read analog data from specified channels
        :param channel: Either int of list of ints that specifies channel to read.
        :param board_number: Board Number
        :return: Returns voltage of channels as either a single float or a list of floats
        """

        # If channels is a single channel
        if type(channel) is int:

            # Initialize array to average data points
            voltage = []

            # Get values for 5-point average
            for _ in range(5):
                # Read data from the channel:
                value_counts = ul.a_in_32(board_number, channel, ULRange.BIP20VOLTS, 0)

                # Convert from counts to volts
                value_volts = ul.to_eng_units_32(board_number, ULRange.BIP20VOLTS, value_counts)

                # Add voltage to main array for average calculation
                voltage.append(value_volts)

            return np.average(voltage)

        # If channels is a single channel
        if type(channel) is list:

            # Initialize list to save channels voltage to
            channel_voltage = []

            for x in channel:

                # Initialize array to average data points
                voltage = []

                # Get values for 5-point average
                for _ in range(5):
                    # Read data from the channel:
                    value_counts = ul.a_in_32(board_number, x, ULRange.BIP20VOLTS, 0)

                    # Convert from counts to volts
                    value_volts = ul.to_eng_units_32(board_number, ULRange.BIP20VOLTS, value_counts)

                    # Add voltage value to single array
                    voltage.append(value_volts)

                # Add 5-point average to respective channel
                channel_voltage.append(np.average(voltage))

            # Returns array with data from all channels
            return channel_voltage


class Plot(Frame):

    def __init__(self, master: Frame | Tk, plot_title="", x_label="", y_label="", data: tuple | list | int = 0, auto_fit=True, follow=120, buffer=3, x_lim: tuple = (0, 1), y_lim: tuple = (0, 1), figure_size=(4, 4), dpi=100):
        """
            Class for plotting data in tkinter.

            Data to be fed into this class should be formatted as follows:

                x = [1, 2, 3, 4, 5]
                y = [1, 2, 3, 4, 5]
                label = "Data"

                data = (x, y, label)

                plot = Plot(root, data)

            OR

                x = [1, 2, 3, 4, 5]
                y = [1, 2, 3, 4, 5]
                label = "Data1"

                data1 = (x, y, label)

                z = [1, 2, 3, 4, 5]
                w = [1, 2, 3, 4, 5]
                label2 = "Data2"

                data2 = (z, w, label2)

                data = [data1, data2]

                plot = Plot(root, data)

            Data can also be added after initialization as follows:

                plot = Plot(Frame)
                plot.update_data(data)

            It is recommended to make a separate frame for the Plot class as follows:

                plot_frame = Frame(master)
                plot_frame.pack()
                plot = Plot(plot_frame)


            :param master: Frame or Tk to place plot on
            :param data: Data to plot as either a tuple or list. Refer to documentation for formatting. Can be initialized after Plot using Plot.update_data(data)
            :param plot_title: Title to be shown on plot - Optional
            :param x_label: abel for x-axis - Optional
            :param y_label: Label for y-axis - Optional
            :param auto_fit: True by default. Will automatically scale plot to fit data. - Optional
            :param follow: Amount to follow x-axis right limit by. Set to 0 to turn off. - Optional
            :param buffer: Padding on y-axis from max and min values. - Optional
            :param x_lim: X-axis limits. A tuple with the format: (min, max) - Optional
            :param y_lim: Y-axis limits. A tuple with the format: (min, max) - Optional
            :param figure_size: Size of plot. A tuple with the format: (horizontal_length, vertical_length) - Optional
            :param dpi: Resolution of the plot. - Optional
            """
        super().__init__(master)

        # Style for plots to use
        style.use('seaborn')

        # Initializes parameters for use throughout class
        self.auto_fit = auto_fit
        self.follow = follow
        self.buffer = buffer

        # Initializes figure
        self.figure = Figure(figure_size, dpi=dpi)

        # Initializes plot
        self.main_plot = self.figure.add_subplot(111)

        # Saves title and axis labels and adds
        self.title = plot_title
        self.x_label = x_label
        self.y_label = y_label
        self.main_plot.set_title(plot_title)
        self.main_plot.set_xlabel(x_label)
        self.main_plot.set_ylabel(y_label)

        # If auto_size is true and data is not empty
        if auto_fit and data != 0:

            # Gets axis limits for data
            limits = self.get_data_limits(data)

            if self.follow == 0:

                # Sets axis limits
                self.main_plot.set_xlim(limits[1], limits[0])
                self.main_plot.set_ylim(limits[3] - self.buffer, limits[2] + self.buffer)

            else:

                # Sets axis limits
                self.main_plot.set_xlim(limits[0] - self.follow, limits[0])
                self.main_plot.set_ylim(limits[3] - self.buffer, limits[2] + self.buffer)


        else:

            # Sets axis limits
            self.main_plot.set_xlim(x_lim[0], x_lim[1])
            self.main_plot.set_ylim(y_lim[0], y_lim[1])

        # Plots data
        if type(data) is tuple:

            # Plots single set of data
            self.main_plot.plot(data[0], data[1], label=data[2])

            # Initializes legend in lower right corner
            self.legend = self.main_plot.legend(loc='lower left')

        if type(data) is list:

            # Plots multiple sets of data
            for i in data:
                self.main_plot.plot(i[0], i[1], label=i[2])

            # Initializes legend in lower right corner
            self.legend = self.main_plot.legend(loc='lower left')


        # Draws figure
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def clear(self):
        """
        Clears plot data without removing title and axes
        """
        # Clears plot data
        self.main_plot.clear()

        # Reinitialize title and axis labels
        self.main_plot.set_title(self.title)
        self.main_plot.set_xlabel(self.x_label)
        self.main_plot.set_ylabel(self.y_label)

    def update_data(self, data, x_lim=(0, 1), y_lim=(0, 1)):

        # Clears previous plot data
        self.clear()

        # If auto_fit is true
        if self.auto_fit:

            # Gets axis limits for data
            limits = self.get_data_limits(data)

            # Is follow is off
            if self.follow == 0:

                # Sets axis limits
                self.main_plot.set_xlim(limits[1], limits[0])
                self.main_plot.set_ylim(limits[3] - self.buffer, limits[2] + self.buffer)

            else:

                # Sets axis limits
                self.main_plot.set_xlim(limits[0] - self.follow, limits[0])
                self.main_plot.set_ylim(limits[3] - self.buffer, limits[2] + self.buffer)

        # If auto_fit is not true use method parameters
        else:

            # Sets axis limits
            self.main_plot.set_xlim(x_lim[0], x_lim[1])
            self.main_plot.set_ylim(y_lim[0], y_lim[1])

        # Plots data
        if type(data) is tuple:
            # Plots single set of data
            self.main_plot.plot(data[0], data[1], label=data[2])
        if type(data) is list:
            # Plots multiple sets of data
            for i in data:
                self.main_plot.plot(i[0], i[1], label=i[2])

        # Initializes legend in lower right corner
        self.legend = self.main_plot.legend(loc='lower left')

        # Applies changes
        self.canvas.draw()

    @staticmethod
    def get_data_limits(data):
        """
        Function to get max and min from data

        :param data: Either tuple or list of tuples in correct format - refer to Plot __init__ documentation.
        :return: Max and min for both x and y in data in the tuple format: (x_maximum, x_minimum, y_maximum, y_minimum)
        """

        # If data is a single set
        if type(data) == tuple:
            return np.max(data[0]), np.min(data[0]), np.max(data[1]), np.min(data[1])

        # If data is multiple sets
        if type(data) == list:

            # Initialize max and min values
            x_maximum = -10**10
            x_minimum = 10**10
            y_maximum = -10 ** 10
            y_minimum = 10 ** 10

            # Checks for max and min in each set and updates overall max and min
            for x in data:

                if np.max(x[0]) > x_maximum:
                    x_maximum = np.max(x[0])
                if np.min(x[0]) < x_minimum:
                    x_minimum = np.min(x[0])

                if np.max(x[1]) > y_maximum:
                    y_maximum = np.max(x[1])
                if np.min(x[1]) < y_minimum:
                    y_minimum = np.min(x[1])

            return x_maximum, x_minimum, y_maximum, y_minimum


class DataHandler:

    @staticmethod
    def export(data: pd.DataFrame(), output_directory_path: str, filename: str, sheet_name="Sheet1"):
        """
        Method to export pandas dataframe to Excel file.
        :param data: Data as a pandas DataFrame
        :param output_directory_path: Path to export file to
        :param filename: Name of file
        :param sheet_name: Name of sheet
        """

        # Formats path if necessary
        if output_directory_path[-1] != '/':
            output_directory_path += '/'

        # Checks if directory exists or not then makes it
        if not os.path.exists(output_directory_path):
            os.makedirs(output_directory_path)

        # Try to write data to given filename
        try:

            # Get path
            path = output_directory_path + filename + ".xlsx"

            # Initializes writer
            writer = pd.ExcelWriter(path, engine='xlsxwriter')

        # If any error occurs, write file labelled "temp xlsx" instead to project directory
        except:

            # Get path
            path = "./MCC-DAQ backup/" + "temp.xlsx"

            # Initializes writer
            writer = pd.ExcelWriter(path, engine='xlsxwriter')

        # Writes data
        data.to_excel(writer, index=False)

        # Auto-fits data to columns
        for column in data:
            column_length = max(data[column].astype(str).map(len).max(), len(column))
            col_idx = data.columns.get_loc(column)
            writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length)

        # Saves data
        writer.close()


# Runs app and updates every 1000ms.
# 1000ms is the minimum recommended refresh time as it takes about 600-800ms to perform operations.
# App will output error to terminal if operation time exceeds refresh rate.
app = App(5000)
app.main_thread()
app.mainloop()
