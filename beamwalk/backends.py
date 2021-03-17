from ThorlabsPM100 import ThorlabsPM100 as ThorlabsPM100_
from ThorlabsPM100 import usbtmc
import pyvisa as visa
import os
import platform
from time import sleep


class ThorlabsPM100:
    def __init__(self):

        self.instr = None

        os.system("cls" if os.name == "nt" else "clear")
        youros = platform.system()
        if youros == "Linux":
            print("You're running Linux")
            """
            The following line is the inst(rument) setup for linx
            """
            self.instr = usbtmc.USBTMC()  # device='/dev/usbtmc0'
        elif youros == "Windows":
            print("---")
            print("You're running Windows")
            """
            The following lines are the inst(rument) setup for linx windows
            """
            rm = visa.ResourceManager()
            for resource in rm.list_resources():
                if resource.startswith("USB0::0x1313::0x807"):
                    print(f"Found Powermeter {resource}")
                    instr = rm.open_resource(resource, timeout=1000)
                    self.instr = ThorlabsPM100_(inst=instr)
                    print(f"Connected to: {resource}")
                    break

        if not self.instr:
            raise ConnectionRefusedError("No Powermeter found.")

        sleep(1)
        self.instr.sense.power.dc.range.auto = "ON"

    def read(self):
        return self.instr.read


class LabDataService:
    def __init__(self, netloc, field):

        import rcyp

        self.field = field
        try:
            host, port = parse_netloc(netloc)
            self.service = rpyc.connect(host, port)
            print(
                f"Connected to {self.service.root.get_service_name()} on port {port}."
            )
        except ConnectionRefusedError:
            print(f"Connection to service at {host}:{port} refused.")

    def read(self):
        data = self.service.root.exposed_get_data(self.field)
        val = data["fields"][self.field]
        return val


def parse_netloc(netloc):
    """
    Split network location pair hostname:port into the hostname and port.

    Parameters
    ----------
    netloc : str or int
        Network location, e.g. localhost:18861. If an int is passed, localhost is
        assumed.

    Returns
    -------
    host : str
    port : int
    """
    split_netloc = netloc.split(":")
    if len(split_netloc) == 2:
        # host:port pair
        host = split_netloc[0]
        port = int(split_netloc[1])
    elif len(split_netloc) == 1:
        # only port
        host = "localhost"
        port = int(split_netloc[0])
    else:
        raise ValueError("'{}' is not a valid location".format(netloc))
    return host, port
