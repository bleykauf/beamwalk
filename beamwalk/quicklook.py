import pandas as pd
import matplotlib.pyplot as plt
import click


@click.command()
@click.argument("filename", type=str)
def look(filename):
    data = pd.read_csv(filename, delimiter="\t", header=0, parse_dates=True)
    data["datetime"] = pd.to_datetime(data["datetime"])
    data = data.set_index("datetime")

    d = (
        200
        * (data["data"].max() - data["data"].min())
        / (data["data"].max() + data["data"].min())
    )
    m = data["data"].mean()
    print("Mean power is {:.6f} W".format(m))
    print("Fluctuations are {:2f} %".format(d))
    data.plot()
    plt.title(filename)
    plt.xlabel("Time in datetime")
    plt.ylabel("Power in W")
    plt.ylim(0, data["data"].max() * 1.05)
    plt.grid()
    plt.legend()
    plt.show()
