import os
import signal
from datetime import datetime
from time import sleep

import click
import numpy as np

from . import backends
from .coupling import Plotter


@click.command()
@click.option("--goal", default=1.0, help="Goal in W")
@click.option("--logging", default=False, help="logging beahviour", is_flag=True)
@click.option("--filename", "--file", default="", help="file/path for logging")
@click.option("--backend", default="tl", help="Backend (tl or lds or random)")
@click.option("--field", default="val", help="(for LabDataService backend only)")
@click.option(
    "--netloc", default="localhost:18862", help="(for LabDataService backend only)"
)
def run(goal, logging, filename, backend, field, netloc):

    os.system("cls" if os.name == "nt" else "clear")

    # completely kills application when ctrl+c is pressed
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # setup power meter
    if backend == "tl":
        power_meter = backends.ThorlabsPM100()
    elif backend == "lds":
        power_meter = backends.LabDataService(netloc, field)
    elif backend == "random":
        power_meter = backends.RandomNumberMeter()

    # data logging
    if logging:
        while not filename:
            filename = input("Specify a filename:\n")
            filename = "{:s}".format(filename)
    else:
        # log everything to /dev/null (cross-platform) if logging deactivated
        filename = os.devnull
    with open(filename, "a") as datafile:
        datafile.write("datetime" + "\t" + "data" + "\n")
    t = 0
    plotter = Plotter(goal=goal)
    size = 500
    x_vec = np.linspace(0, 1, size + 1)[0:-1]
    y_vec = np.zeros(size)
    line1 = []
    linemax = []
    linegoal = []
    with open(filename, "a") as datafile:
        while True:
            if plotter.request_shutdown:
                break
            t += 1
            val = power_meter.read()

            # log to file or /dev/null
            datafile.write(str(datetime.now()) + "\t {:.3e} \n".format(val))
            if val > plotter.y_max:
                plotter.y_max = val
            y_vec[-1] = val
            line1, linemax, linegoal = plotter.plot(
                x_vec,
                y_vec,
                plotter.y_max,
                line1,
                linemax,
                linegoal,
                plotter.goal,
                plotter.rescale,
                plotter.timewarp,
                pause_time=plotter.pause_time,
            )
            y_vec = np.append(y_vec[1:], 0.0)
