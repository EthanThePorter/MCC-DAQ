"""
File:                       USB2416_a_out.py

Library Call Demonstrated:  mcculw.ul.a_out().

Purpose:                    control the analog output

Demonstration:              analog out range from -10V to +10V is .1V steps.

Other Library Calls:        mcculw.ul.from_eng_units()
                            mcculw.ul.flash_LED()
                            mcculw.ul.get_board_name()

Special Requirements:       requires a volt meter or oscilloscope to see
                            data output.

Notes:                      No board detection or device discovery in this app.
                            board must be assigned in InstaCal as Board 0.
                            This example is made simple so as not
                            to be confusing (that was the hope anyway)
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from time import sleep

from mcculw import ul
from mcculw.enums import ULRange  # , DigitalIODirection, ErrorCode


def run_example():
    device_to_show = "USB-2416-4AO"
    board_num = 0
    channel_num = 0

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
        # set analog out from -10V to 10V in 0.1V steps...
        a_out_volts = -10
        while a_out_volts <= 10:
            a_out_counts = ul.from_eng_units(board_num, ULRange.BIP10VOLTS, a_out_volts)
            ul.a_out(board_num, channel_num, ULRange.BIP10VOLTS, a_out_counts)
            txt = "setting AOut{:d} to {:.1f} volts as {:d} counts."
            print(txt.format(channel_num, a_out_volts, a_out_counts))
            a_out_volts += 0.1
            sleep(.5)

    except Exception as e:
        print('\n', e)

    finally:
        # set analog out to 0 V at end
        print("\nSetting analog out channel to 0 VDC.")
        ul.v_out(board_num, channel_num, ULRange.BIP10VOLTS, 0)


if __name__ == '__main__':
    run_example()
