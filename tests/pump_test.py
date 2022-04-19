# Used by Controller
from __future__ import absolute_import, division, print_function
from builtins import *
from mcculw import ul
from mcculw.enums import ULRange, InfoType, BoardInfo, AiChanType, AnalogInputMode, TcType, TempScale, TInOptions
import numpy as np

import time


class Controller:
    """
    Set of functions to interact with MCC control board.
    """
    @staticmethod
    def initialize_thermocouple_read(channel: int | list[int], board_number=0, rate=60, thermocouple_type=TcType.K):

        # If channel is single value setup single channel
        if type(channel) is int:
            # Set channel type to TC (thermocouple)
            ul.set_config(
                InfoType.BOARDINFO, board_number, channel, BoardInfo.ADCHANTYPE,
                AiChanType.TC)
            # Set thermocouple type to type K
            ul.set_config(
                InfoType.BOARDINFO, board_number, channel, BoardInfo.CHANTCTYPE,
                thermocouple_type)
            # Set the temperature scale to Celsius
            ul.set_config(
                InfoType.BOARDINFO, board_number, channel, BoardInfo.TEMPSCALE,
                TempScale.CELSIUS)
            # Set data rate
            ul.set_config(
                InfoType.BOARDINFO, board_number, channel, BoardInfo.ADDATARATE, rate)

        # If channel is list setup every channel in list
        if type(channel) is list:
            for i in channel:
                # Set channel type to TC (thermocouple)
                ul.set_config(
                    InfoType.BOARDINFO, board_number, i, BoardInfo.ADCHANTYPE,
                    AiChanType.TC)
                # Set thermocouple type to type K
                ul.set_config(
                    InfoType.BOARDINFO, board_number, i, BoardInfo.CHANTCTYPE,
                    thermocouple_type)
                # Set the temperature scale to Celsius
                ul.set_config(
                    InfoType.BOARDINFO, board_number, i, BoardInfo.TEMPSCALE,
                    TempScale.CELSIUS)
                # Set data rate
                ul.set_config(
                    InfoType.BOARDINFO, board_number, i, BoardInfo.ADDATARATE, rate)

    @staticmethod
    def thermocouple_instantaneous_read(channel: int | list[int], board_number=0):
        """
        Reads thermocouple.

        :param board_number: Board number
        :param channel: Desired channel to read
        :return: Temperature in celsius
        """
        # Configure options for thermocouple read
        options = TInOptions.NOFILTER

        # If channel is single value read and return single channel
        if type(channel) is int:
            return ul.t_in(board_number, channel, TempScale.CELSIUS, options)

        # If channel is list read and return list for every channel in list
        if type(channel) is list:
            return [ul.t_in(board_number, x, TempScale.CELSIUS, options) for x in channel]

    @staticmethod
    def initialize_analog_read(channel: int | list[int], board_number=0, rate=60):
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
    def analog_read(channel: int | list[int], board_number=0):
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

    @staticmethod
    def analog_out(VDAC_channel: int | list[int], voltage: float, board_number=0):
        """
        Method to set channel to output an analog voltage
        :param VDAC_channel: VDAC Channel to set
        :param voltage: Desired Voltage
        :param board_number: Board to Control
        """

        # If single channel is entered
        if type(VDAC_channel) is int:

            # Converts voltage to MCC counts and sets channel
            a_out_counts = ul.from_eng_units(board_number, ULRange.BIP10VOLTS, voltage)
            ul.a_out(board_number, VDAC_channel, ULRange.BIP10VOLTS, a_out_counts)

        # If list of channels in entered
        if type(VDAC_channel) is list:

            # For each channel in list
            for c in VDAC_channel:

                # Converts voltage to MCC counts and sets channel
                a_out_counts = ul.from_eng_units(board_number, ULRange.BIP10VOLTS, voltage)
                ul.a_out(board_number, c, ULRange.BIP10VOLTS, a_out_counts)


# Channel for pump
VDAC_channel = 1
voltage = 9.6059
Controller.analog_out(VDAC_channel, voltage)

x = input("Enter any key to stop: ")

# Turn off pump by setting to low voltage
Controller.analog_out(VDAC_channel, 0)


