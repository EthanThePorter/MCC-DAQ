"""
File:                       USB2416_a_in_32.py

Library Call Demonstrated:  mcculw.ul.a_in_32().

Purpose:                    Setup and read from an analog input, one sample at a time.

Demonstration:              How to configure and read voltage value from device.

Other Library Calls:        mcculw.ul.flash_LED()
                            mcculw.ul.set_config()
                            mcculw.ul.a_chan_input_mode()
                            mcculw.ul.to_eng_units_32()

Special Requirements:       Connect an analog voltage source to CH0H and AGND
                            terminals of the USB-2408 series or, connect the
                             +5V output of USB-2408 CH0H.

Notes:                      No board detection or device discovery in this app.
                            Device must be assigned in InstaCal as Board 0.
                            This example is made simple so as not to
                            be confusing (that was the hope anyway).
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import ULRange, InfoType, BoardInfo, AiChanType, AnalogInputMode

import numpy as np

import time


def run_example():
    board_num = 0

    try:

        for _ in range(10):

            voltage = []

            for _ in range(5):

                # select a channel
                channel = 2
                # configure the channel for voltage
                ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADCHANTYPE, AiChanType.VOLTAGE)

                # Set channel to single ended input mode
                ul.a_chan_input_mode(board_num, channel, AnalogInputMode.DIFFERENTIAL)

                # Set channel rate
                ul.set_config(InfoType.BOARDINFO, board_num, channel, BoardInfo.ADDATARATE, 60)

                # Read data from the channel:
                value_counts = ul.a_in_32(board_num, channel, ULRange.BIP20VOLTS, 0)

                # Convert from counts to volts
                value_volts = ul.to_eng_units_32(board_num, ULRange.BIP20VOLTS, value_counts)

                voltage.append(value_volts)

            print(np.average(voltage))

    except Exception as e:
        print('\n', e)



def initialize_analog_read(channel: int | list, board_number=0, range=ULRange.BIP20VOLTS, options=0, rate=60):
    """
    Initializes channels to read by analog
    :param channel: Channel or list of channels to be initialized
    :param board_number: Number of board
    :param range: Voltage Range. 20V range is recommended to reduce data noise.
    :param options: Depreciated parameter.
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


channel = [2, 3]

initialize_analog_read(channel)

voltage = analog_read(channel)

print(voltage)
