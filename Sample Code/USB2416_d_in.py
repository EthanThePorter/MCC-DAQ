"""
File:                       USB2416_d_in.py

Library Call Demonstrated:  mcculw.ul.d_in().

Purpose:                    Read the digital port, one digital bit at a time.

Demonstration:              Monitor the entire FirstPortA, all 8 bits

Other Library Calls:        mcculw.ul.flash_LED()

Special Requirements:       Connect any digital bit to +5V or DGND terminal of the USB-2408 series
                            or, use an external signal source.

Notes:                      No board detection or device discovery in this app.
                            board must be assigned in InstaCal as Board 0.
                            This example is made simple so as not to
                            be confusing (that was the hope anyway)
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from time import sleep

from mcculw import ul
from mcculw.enums import DigitalPortType  # , DigitalIODirection, ErrorCode


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
            print("{0} found as Board number {1}.".format(board_name, board_num))
            ul.flash_led(board_num)

        else:
            # Board 0 is NOT desired device...
            print("\nNo {0} series found as Board 0. Please run InstaCal.".format(device_to_show))
            return

    try:
        # Read the port:
        port_value = ul.d_in(board_num, DigitalPortType.FIRSTPORTA)
        print("Port value:  {0}".format(port_value))

        # Decode the port and return the bit values...
        for bit_num in range(8):
            bit_value = 0
            if port_value & (2 ** bit_num) == 2 ** bit_num:
                bit_value = 2 ** bit_num

            print("Reading bit{0}: value of {1} to the port.".format(bit_num, bit_value))

    except Exception as e:
        print('\n', e)


if __name__ == '__main__':
    run_example()
