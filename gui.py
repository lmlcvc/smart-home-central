"""Gui

This file contains the app (Tk) class, and the main method which starts the GUI and serial communication.

Running both simultaneously makes use of multithreading.
If serial communication is available, a separate thread is started
from file_handler.py to run the serial communication.

This file is the starting point of the app. It creates the folder and files sensor readings will be stored into,
starts serial communication with the Arduino Micro, and starts the app.
It also defines all methods necessary for runtime app use.
"""
import threading
import tkinter as tk
import matplotlib

import file_handler as fh
import pages as pg
import constants

matplotlib.use("TkAgg")


class SensorCentral(tk.Tk):
    """
        A class used to create the root of Tk interface.

        Attributes
        ----------
        frames : dict
            Contains all pages in app.
            key - SensorPage or StartPage (child) object
            value - instance of that page in app

        Methods
        -------
        show_frame(self, content)
            Raise the frame passed as 'content'.

        app_update(self)
            Call update on all sensor pages and start page.
            As specified in main, this is called every 60 s.
            Additionally, this is called on every update called from update page.
    """

    frames = {}

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, constants.APP_NAME)

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w, h))

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for page in [pg.StartPage, pg.TMP116Page, pg.HDC2010Page, pg.OPT3001Page, pg.DPS310Page, pg.UpdatePage]:
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(pg.StartPage)

    def show_frame(self, content):
        frame = self.frames[content]
        frame.tkraise()

    def app_update(self):
        pg.StartPage.update_start_data(self.frames[pg.StartPage])

        pg.TMP116Page.update_data(self.frames[pg.TMP116Page],
                                  [constants.tmp116_csv], [constants.temp_string], [constants.temp_measurement])
        pg.HDC2010Page.update_data(self.frames[pg.HDC2010Page],
                                   [constants.hdc2010_temp_csv, constants.hdc2010_hum_csv],
                                   [constants.temp_string, constants.hum_string],
                                   [constants.temp_measurement, constants.hum_measurement]
                                   )
        pg.OPT3001Page.update_data(self.frames[pg.OPT3001Page],
                                   [constants.opt3001_csv], [constants.light_string], [constants.light_measurement])
        pg.DPS310Page.update_data(self.frames[pg.DPS310Page],
                                  [constants.dps310_temp_csv, constants.dps310_pressure_csv],
                                  [constants.temp_string, constants.pressure_string],
                                  [constants.temp_measurement, constants.pressure_measurement]
                                  )


def call_repeatedly(interval, func, *args):
    """ Call func(*args) every {interval} seconds. """
    stopped = threading.Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)

    threading.Thread(target=loop).start()
    return stopped.set


if __name__ == '__main__':
    fh.folder_prep()  # prepare csv folder
    fh.connect_to_serial()  # start serial communication if available

    app = SensorCentral()  # start the app
    cancel_future_calls = call_repeatedly(10, app.app_update, )  # call for repeated app update
    app.iconbitmap(constants.ICON_PATH)  # set app icon
    app.mainloop()  # enter main app loop after repeated calls instantiated

    cancel_future_calls()  # cancel future calls after window closes
