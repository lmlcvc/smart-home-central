""" File handler

This file contains methods used for file and directory handling, for purposes of running this application.

It can also be imported as a module and contains the following
functions:
    * folder_prep - makes CSV folder and/or files on specified location, if necessary
    * wait_for_file_input - waits for file to be not-empty before making plots
    * impl_circular_buffer - treats each sensor's CSV as a circular buffer with MAX_ROWS size
    * store_to_csv - listens to serial port and writes values to appropriate CSV files
"""

import os
from datetime import datetime

from constants import *


def folder_prep():
    """ Prepare and/or modify folder and file locations for sensor readings. """

    # make csv folder if it doesn't exist
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)

    # populate csv folder with specified files if it's empty
    if len(os.listdir(csv_folder)) == 0:
        open(tmp116_csv, 'a').close()
        open(hdc2010_temp_csv, 'a').close()
        open(hdc2010_hum_csv, 'a').close()
        open(opt3001_csv, 'a').close()
        open(dps310_temp_csv, 'a').close()
        open(dps310_pressure_csv, 'a').close()


def wait_for_file_input(filepath):
    """ Wait for file to be non-empty before plotting its data.
        This is to avoid a possible bug when plotting

        Arguments:
            filepath - location of the file waiting for input
    """

    while ((os.path.exists(filepath) and os.path.getsize(filepath) == 0)
           or not os.path.exists(filepath)):
        pass


def impl_circular_buffer(filepath, buff_size=MAX_ROWS):
    """ Treat csv file as a circular buffer.

        Arguments:
            filepath - location of the file being modified
            buff_size - size of buffer depending on sampling frequency; default MAX_ROWS
    """

    # light and pressure measures require higher sampling rates (more records)
    if (filepath == opt3001_csv) or (filepath == dps310_pressure_csv):
        buff_size = MAX_ROWS_OPT_PRES

    # open file, store its lines to list
    with open(filepath, 'r') as file:
        lines = []
        for row in file.readlines():
            lines.append(row)
        num_rows = len(lines)
    file.close()

    # remove any oldest lines that exceed maximum buffer size and write result to file
    if num_rows > buff_size:
        extra_rows = num_rows - buff_size
        with open(filepath, 'w') as file:
            file.writelines(lines[:1] + lines[(extra_rows + 1):])
    file.close()
    return


def store_to_csv():
    """ Store lines from serial port to respective CSV files. """

    with open(tmp116_csv, 'a', newline='') as tmp116_file, \
            open(hdc2010_temp_csv, 'a', newline='') as hdc2010_temp_file, \
            open(hdc2010_hum_csv, 'a', newline='') as hdc2010_hum_file, \
            open(opt3001_csv, 'a', newline='') as opt3001_file, \
            open(dps310_temp_csv, 'a', newline='') as dps310_temp_file, \
            open(dps310_pressure_csv, 'a', newline='') as dps310_pressure_file:

        for i in range(NUM_OF_SENSORS):  # TODO: change to while-loop because of different sampling rates
            line = serial.readline()  # read a byte string

            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            if line:
                string = line.decode()  # convert the byte string to a unicode string
                split_string = string.split(', ')

                # choose write file location based on sensor name and value
                # add current time to record
                if split_string[0] == 'TMP116':
                    tmp116_file.write(dt_string + ', ' + string)
                elif split_string[0] == 'HDC2010' and split_string[1] == 'temperature':
                    hdc2010_temp_file.write(dt_string + ', ' + string)
                elif split_string[0] == 'HDC2010' and split_string[1] == 'humidity':
                    hdc2010_hum_file.write(dt_string + ', ' + string)
                elif split_string[0] == 'OPT3001':
                    opt3001_file.write(dt_string + ', ' + string)
                elif split_string[0] == 'DPS310' and split_string[1] == 'temperature':
                    dps310_temp_file.write(dt_string + ', ' + string)
                elif split_string[0] == 'DPS310' and split_string[1] == 'pressure':
                    dps310_pressure_file.write(dt_string + ', ' + string)