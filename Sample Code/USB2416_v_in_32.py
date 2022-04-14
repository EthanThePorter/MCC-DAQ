"""
File:                       USB2416_v_in_32.py

Library Call Demonstrated:  mcculw.ul.v_in_32().

Purpose:                    Setup and read from an analog input, one sample at a time.

Demonstration:              How to configure and read voltage value from device.

Other Library Calls:        mcculw.ul.flash_LED()
                            mcculw.ul.set_config()
                            mcculw.ul.a_chan_input_mode()

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


def run_example():
    device_to_show = "USB-2416"
    board_num = 0

    # Verify board is Board 0 in InstaCal.  If not, show message...
    print("Looking for Board 0 in InstaCal to be {0} series...".format(device_to_show))

    try:
        # Get the devices name...
        board_name = ul.get_board_name(board_num)

    except Exception as e:
        if ul.ErrorCode(1):
            # No board at that number throws error
            print("\nNo board found at Board 0.")
            print(e)
            return

    else:
        if device_to_show in board_name:
            # Board 0 is the desired device...
            print("{0} found as Board number {1}.\n".format(board_name, board_num))
            ul.flash_led(board_num)

        else:
            # Board 0 is NOT desired device...
            print("\nNo {0} series found as Board 0. Please run InstaCal.".format(device_to_show))
            return

    try:
        # select a channel
        channel = 0
        # configure the channel for voltage
        ul.set_config(InfoType.BOARDINFO, board_num, channel,
                      BoardInfo.ADCHANTYPE, AiChanType.VOLTAGE)

        # Set channel to single ended input mode
        ul.a_chan_input_mode(board_num, channel, AnalogInputMode.SINGLE_ENDED)

        # Read data from the channel:
        options = 0 # reserved for future use
        value_volts = ul.v_in_32(board_num, channel, ULRange.BIP10VOLTS, options)
        print("Channel{:d}: {:.3f} volts DC".format(channel, value_volts))

    except Exception as e:
        print('\n', e)


if __name__ == '__main__':
    run_example()
