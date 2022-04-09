from __future__ import absolute_import, division, print_function
from builtins import *
from mcculw import ul
from mcculw.enums import ULRange, InfoType, BoardInfo, AiChanType, AnalogInputMode, TcType, TempScale, TInOptions

import numpy as np

from tkinter import *
from tkinter import ttk

# Imports for Plot class
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style

import time


class App(Tk):

    def __init__(self, refresh_time, *args, **kwargs):
        """
        Main App class

        :param refresh_time: Time in ms for refresh
        """
        Tk.__init__(self, *args, **kwargs)

        # Initializes start time
        self.start_time = time.time()

        # Initializes time to update labels
        self.refresh_time = refresh_time

        # Window settings
        self.title('MCC DAQ')
        self.config(padx=10, pady=10)
        self.config(background='white')
        self.iconbitmap('assets/uwicon.ico')

        # Channels to create labels for
        self.channels = [0, 1, 8, 12, 13]

        # Configure channels to read thermocouples
        Controller.initialize_thermocouple_read(self.channels)

        # Initializes lists for temperature and time to be saved to
        self.temperature = [[] for x in self.channels]
        self.runtime = []

        # Initializes max/min values for graph
        self.max_temperature = -1000
        self.min_temperature = 1000

        # Create plot
        self.plot_frame = Frame(self)
        self.plot_frame.grid(row=0, column=0)
        self.plot = Plot(self.plot_frame, "Channel Temperature Data", "Time (s)", "Temperature (°C)", figure_size=(4, 6))


    def update_all(self):

        # Gets start time of function for metrics
        update_runtime_start = time.time()

        # Gets temperatures and round them
        current_temperatures = np.round(Controller.thermocouple_instantaneous_read(self.channels), 1)

        #Gets time and rounds - adds to runtime array
        relative_time = np.round(time.time() - self.start_time, 1)
        self.runtime.append(relative_time)

        # Appends temperature data to main array and checks for new max and min
        for x in range(len(self.channels)):

            # Appends current temperatures to a 2D list
            self.temperature[x].append(current_temperatures[x])

            # Updates max and min temperature
            if current_temperatures[x] > self.max_temperature:
                self.max_temperature = current_temperatures[x]
            if current_temperatures[x] < self.min_temperature:
                self.min_temperature = current_temperatures[x]

        # Formats data for plotting - refer to Plot class for more information.
        data = []
        for x in range(len(self.channels)):
            data.append((self.runtime, self.temperature[x], "Channel " + str(self.channels[x]) + ": " + str(current_temperatures[x]) + "°C"))

        # Updates plot
        self.plot.update_data(data)

        # Gets time taken to run function and outputs to terminal
        update_runtime_finish = (time.time() - update_runtime_start) * 1000
        #print(str(update_runtime_finish) + "ms")

        # Subtracts time took to run overall method for consistent data points
        adjusted_time = int(abs(self.refresh_time - update_runtime_finish))

        # End of function command to repeat,
        self.after(adjusted_time, self.update_all)


class Controller:
    """
    Set of functions to interact with MCC control board.
    """

    @staticmethod
    def initialize_read_voltage(channel, board_num=0, rate=60):
        """
        Initializes channel to read voltage.

        :param board_num: Board Number
        :param channel: Channel to initialize - either int or list of ints
        :param rate: Rate in hertz of how many scans per second
        """
        if type(channel) == int:
            # Configure to read voltage
            ul.set_config(
                InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE,
                AiChanType.VOLTAGE)
            # Set to differential input mode
            ul.a_chan_input_mode(board_num, channel, AnalogInputMode.DIFFERENTIAL)
            # Set data rate to 60Hz
            ul.set_config(
                InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE, rate)

        if type(channel) == list:
            for i in channel:
                # Configure to read voltage
                ul.set_config(
                    InfoType.BOARDINFO, board_num, i, BoardInfo.ADCHANTYPE,
                    AiChanType.VOLTAGE)
                # Set to differential input mode
                ul.a_chan_input_mode(board_num, i, AnalogInputMode.DIFFERENTIAL)
                # Set data rate to 60Hz
                ul.set_config(
                    InfoType.BOARDINFO, board_num, i, BoardInfo.ADDATARATE, rate)

    @staticmethod
    def voltage_instantaneous_read(channel, board_num=0, ai_range=ULRange.BIP5VOLTS, options=0):
        """
        Reads voltage from desired channel or channels.

        :param board_num: Board number
        :param channel: Desired channel to read
        :param ai_range: Voltage Range
        :param options: For future use
        :return: Voltage from Channel
        """
        if type(channel) is int:
            return ul.v_in_32(board_num, channel, ai_range, options)

        if type(channel) is list:
            return [ul.v_in_32(board_num, x, ai_range, options) for x in channel]

    @staticmethod
    def convert_voltage_to_temperature(voltage, channel):
        """
        Converts voltage in V to temperature in degrees Celsius.

        :param channel: Channel read so calibration value can be applied
        :param voltage: Voltage in V
        :return: Temperature in degrees C
        """
        # Calibration values for thermocouples
        channel_calibration_values = {8: [0.0012796027, 0, 0.1331613]}

        calibration = channel_calibration_values[channel]
        return np.round(24.316564 * (voltage + calibration[0]) * 1000 - 1.090500 - calibration[1], 2)

    @staticmethod
    def calibrate(actual_temperature, average_voltage):
        """
        Calibration function designed to calibrate K-type thermocouples.

        :param actual_temperature: Real temperature taken from separate device.
        :param average_voltage: Average voltage of the thermocouple
        :return: Returns value to add to the voltage output of the thermocouple to obtain a correct reading.
        """
        return (actual_temperature * 0.04111467 + 0.05058242) / 1000 - average_voltage

    @staticmethod
    def initialize_thermocouple_read(channel, board_num=0, rate=60, thermocouple_type=TcType.K):

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
    def thermocouple_instantaneous_read(channel, board_num=0):
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
    def thermocouple_average_read(channel, number_of_runs_to_average, board_num=0):
        """
        Function to take average of a specified number of thermocouple readings
        :param board_num: Board number
        :param channel: Either single channel or list of channels
        :param number_of_runs_to_average: Runs to average
        :return: Either averaged single value or list of thermocouple readings
        """
        # If channel is single value
        if type(channel) is int:

            # Creates 1D array of temperature vales with length equal to number_of_runs_to_average, then returns average
            temperature_array = [Controller.thermocouple_instantaneous_read(channel, board_num) for x in
                                 range(number_of_runs_to_average)]
            return np.average(temperature_array)

        if type(channel) is list:
            average_temperature_array = []
            for i in channel:
                temperature_array = [Controller.thermocouple_instantaneous_read(channel, board_num) for x in
                                     range(number_of_runs_to_average)]
                print(temperature_array)
                average_temperature_array.append(np.average(temperature_array))
            return average_temperature_array


class Plot(Frame):

    def __init__(self, master: Frame | Tk, plot_title="", x_label="", y_label="", data=0, auto_fit=True, follow=120, buffer=3, x_lim: tuple = (0, 1), y_lim: tuple = (0, 1), figure_size=(4, 4), dpi=100):
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

        :param data: Either tuple or list of tuples in correct format
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

                if np.max(x[1]) > y_minimum:
                    y_maximum = np.max(x[1])
                if np.min(x[1]) < y_minimum:
                    y_minimum = np.min(x[1])

            return x_maximum, x_minimum, y_maximum, y_minimum


# Runs app and updates every 500ms
app = App(500)
app.update_all()
app.mainloop()
