from ThorlabsPM100 import ThorlabsPM100, usbtmc
import pyvisa as visa
import os
import platform
from time import sleep


class PowerMeter:
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
                    self.instr = ThorlabsPM100(inst=instr)
                    print(f"Connected to: {resource}")
                    break

        if not self.instr:
            raise ConnectionRefusedError("No Powermeter found.")

        sleep(1)
        self.instr.sense.power.dc.range.auto = "ON"

    def read(self):
        return self.instr.read
