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

        import rpyc

        self.field = field
        try:
            host, port = self._parse_netloc(netloc)
            self.service = rpyc.connect(host, port)
            print(
                f"Connected to {self.service.root.get_service_name()} on port {port}."
            )
        except ConnectionRefusedError:
            print(f"Connection to service at {host}:{port} refused.")

    def read(self):
        # NOTE: LabDataService expects a list of fields
        data = self.service.root.exposed_get_data([self.field])
        val = data["fields"][self.field]
        return val

    def _parse_netloc(netloc):
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


class ADBox:
    def __init__(self, addr="ASRL5::INSTR", channel=0):
        self.channel = channel
        rm = visa.ResourceManager("@py")
        self.adbox = rm.open_resource(addr, baud_rate=38400)
        self.adbox.timeout = 100

    offset = [
        0.0,
        4.15745e6,
        4.16222e6,
        4.15324e6,
        4.17488e6,
        4.15419e6,
        4.16251e6,
        0.0,
    ]
    scale = [
        1.0e-9,
        -2.82970703125e-05,
        -3.847431640625e-05,
        -3.847431640625e-05,
        -2.046484375e-05,
        -2.987021484375e-05,
        -3.530615234375e-05,
        1.0,
    ]

    def read(self):

        valid_data = False
        while not valid_data:
            # msg1 contains only the initial message CH *, \n and \r and sometimes some
            # of the first returned values, as work around combine strings and filter
            # afterwards
            self.adbox.write("CH MCP * \r")
            msg = ""
            try:
                # read buffer until empty
                while True:
                    msg += self.adbox.read()
            except visa.errors.VisaIOError:
                # if buffer is empty
                num_and_semicolon = set("0123456789;")
                msg = "".join(c for c in msg if c in num_and_semicolon)
                msg = msg.rstrip().split(";")
                msg = list(filter(None, msg))  # filter out empty substrings

            data = list(map(int, msg))  # convert str to list of int

            if len(data) == 8:
                # check data consistency, if something went wrong
                valid_data = True

        # only one channel relevant
        value = data[self.channel]
        value = (value - self.offset[self.channel]) * self.scale[self.channel]
        return value
