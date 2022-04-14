"""
File:                       USB2416_d_out.py

Library Call Demonstrated:  mcculw.ul.d_out().

Purpose:                    control the digital port, one digital bit at a time.

Demonstration:              Control of the entire FirstPortA, all 8 bits

Other Library Calls:        mcculw.ul.flash_LED()

Special Requirements:       The USB-2408 series uses Open Drain technology for
                            digital output, meaning true values turn bit off (0 V),
                            and false values turn bits on (+5 V).

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
        # Turn on one bit of the board in sequence...
        for bit_num in range(8):
            print("Controlling bit: {0}, writing value of {1} to the port.".format(bit_num, 2 ** bit_num))
            ul.d_out(board_num, DigitalPortType.FIRSTPORTA, 2 ** bit_num)
            sleep(1)

    except Exception as e:
        print('\n', e)

    finally:
        # set all bits to off at end
        ul.d_out(board_num, DigitalPortType.FIRSTPORTA, 0)


if __name__ == '__main__':
    run_example()
