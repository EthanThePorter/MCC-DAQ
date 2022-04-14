"""
File:                       USB2416_c_in_32.py

Library Call Demonstrated:  mcculw.ul.c_in_32().

Purpose:                    control the analog output

Demonstration:              analog out range from -10V to +10V is .1V steps.

Other Library Calls:        mcculw.ul.flash_LED()
                            mcculw.ul.get_board_name()
                            mcculw.ul.c_clear()

Special Requirements:       Requires a jumper installed from DIO0 to CTR0
                            as counter source.

Notes:                      No board detection or device discovery in this app.
                            board must be assigned in InstaCal as Board 0.
                            This example is made simple so as not
                            to be confusing (that was the hope anyway)
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from time import sleep

from mcculw import ul
from mcculw.enums import DigitalPortType


def run_example():
    device_to_show = "USB-2416"
    board_num = 0
    counter_number = 0
    counter_value = 0

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
        # Clear the counter (reset to 0) read the counter to confirm...
        ul.c_clear(board_num, counter_number)
        counter_value = ul.c_in_32(board_num, counter_number)

        while counter_value < 100:
            # read the counter...
            counter_value = ul.c_in_32(board_num, counter_number)
            txt = "Reading Ctr{:d}:  {:d} counts."
            print(txt.format(counter_number, counter_value))
            # increment the counter 10x using DIO0 to create events...
            for digital_increment in range (10):
                ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, 0, 1)
                ul.d_bit_out(board_num, DigitalPortType.FIRSTPORTA, 0, 0)
            sleep(.25)

    except Exception as e:
        print('\n', e)

    finally:
        # final value in counter at end
        counter_value = ul.c_in_32(board_num, counter_number)
        txt = "\nFinal reading Ctr{:d}:  {:d} counts."
        print(txt.format(counter_number, counter_value))


if __name__ == '__main__':
    run_example()
