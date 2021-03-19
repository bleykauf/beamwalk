import matplotlib.pyplot as plt
import numpy as np
from ballpark import business


class Plotter:
    def __init__(self, goal=1):
        """
        Init the plotter.
        Set some variables.
        Wait for keys to be pressed
        """
        self.y_max = 0.0
        self.rescale = False
        self.goal = goal
        self.timewarp = False
        self.pause_time = 0.01
        plt.ion()
        self.fig = plt.figure(figsize=(15, 8))

        # if the figure is closed, request a shutdown of the app
        self.fig.canvas.mpl_connect("close_event", self.figure_closed)
        self.request_shutdown = False

        # scaling of figure with key_press_event
        self.fig.canvas.mpl_connect("key_press_event", self.on_press_reaction)

    def on_press_reaction(self, event):
        """
        This function allows rescaling of graph by adjusting the goal
        """
        # print('detsroy the mainframe', event.key)
        if event.key == "0":
            self.y_max = 0.0
        if event.key == "1":
            self.rescale = True
            self.goal *= 10
        if event.key == "2":
            self.rescale = True
            self.goal *= 0.1
        if event.key == "3":
            self.rescale = True
            self.goal *= 1.1
        if event.key == "4":
            self.rescale = True
            self.goal *= 0.9
        if event.key == "5":
            self.timewarp = True
            self.pause_time *= 10
        if event.key == "6":
            self.timewarp = True
            self.pause_time *= 0.1
            if self.pause_time < 0.01:
                print("Speed limit is 10 ms to avoid timeouts...")
                self.pause_time = 0.01

    def plot(
        self,
        x_vec,
        y1_data,
        y_max,
        line1,
        linemax,
        linegoal,
        goal,
        rescale,
        timewarp,
        identifier="",
        pause_time=0.01,
    ):
        """
        Plots and refreshes the Figure
        """
        if line1 == []:
            # this is the call to matplotlib that allows dynamic plotting
            goal_vec = np.ones(len(x_vec)) * goal

            ax = self.fig.add_subplot(111)
            # add info on usage in figure
            textstr = "\n".join(
                (
                    r"Scaling:",
                    r"1: goal x10",
                    r"2: goal x0.1",
                    r"3: goal x1.1",
                    r"4: goal x0.9",
                    r"5: time step x10",
                    r"6: time step x0.1",
                    r"0: reset max bar",
                    r"hit s to save a screenshot",
                )
            )
            props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
            ax.text(
                0.05,
                0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=14,
                verticalalignment="top",
                bbox=props,
            )

            # create a variable for the line so we can later update it
            # (line1,) = ax.fill_between(
            #     x_vec, y1_zeros, y1_data, "-o", color="C0", alpha=0.8
            # )
            (linemax,) = ax.plot(x_vec, y1_data, "--", color="C1", linewidth=6)
            (line1,) = ax.plot(
                x_vec, y1_data, "-o", color="C0", linewidth=6, markersize=6
            )
            (linegoal,) = ax.plot(x_vec, goal_vec, "--", color="C2", linewidth=6)
            # update plot label/title
            # plt.ylabel('Signal')
            # plt.xlabel('Time')
            plt.title("Title: {}".format(identifier))
            plt.ylim(0, goal * 1.05)
            plt.grid(True)
            plt.tick_params(
                axis="both",  # changes apply to the x-axis
                which="both",  # both major and minor ticks are affected
                bottom=False,  # ticks along the bottom edge are off
                top=False,  # ticks along the top edge are off
                labelbottom=False,
                right=False,
                left=False,
                labelleft=False,
            )
            self.fig.text(0.15, 0.95, "Goal:", color="grey", fontsize=20)
            self.fig.text(0.35, 0.95, "Current:", color="grey", fontsize=20)
            self.fig.text(0.65, 0.95, "Maximum:", color="grey", fontsize=20)
            plt.show()

        if self.rescale:
            plt.ylim(0, goal * 1.05)
            goal_vec = np.ones(len(x_vec)) * goal
            linegoal.set_ydata(goal_vec)

        # after the figure, axis and line are created, we only need to update the y-data
        line1.set_ydata(y1_data)

        y_max_vec = np.ones(len(x_vec)) * y_max
        linemax.set_ydata(y_max_vec)  # np.ones(len(y1_data))*ymax
        y_max = float(y_max)
        y_act = float(y1_data[-1])
        # replace zero value to acoid math domain error in ballpark package
        if y_act < 1e-12:
            y_act = 1e-12
        c_eff_max = y_max / goal
        c_eff_act = y_act / goal

        plt.title(
            business(goal, precision=3, prefix=True)
            + "W     "
            + business(y_act, precision=3, prefix=True)
            + "W "
            + "({:.0%})     ".format(c_eff_act)
            + business(y_max, precision=3, prefix=True)
            + "W "
            + "({:.0%})".format(c_eff_max),
            fontsize=40,
            color="C3",
        )

        # adjust limits if new data goes beyond bounds
        # if (
        #     np.min(y1_data) <= line1.axes.get_ylim()[0]
        #     or np.max(y1_data) >= line1.axes.get_ylim()[1]
        # ):
        #     plt.ylim(
        #         [np.min(y1_data) - np.std(y1_data), np.max(y1_data) + np.std(y1_data)]
        #     )
        # this pauses the data so the figure/axis can catch up - the amount of pause can
        # be altered above
        plt.pause(pause_time)

        # return line so we can update it again in the next iteration
        return (line1, linemax, linegoal)

    def figure_closed(self, *args):
        """
        Closes the programm when Figure windows is closed
        """
        plt.ioff()
        self.request_shutdown = True
