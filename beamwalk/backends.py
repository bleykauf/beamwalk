from ThorlabsPM100 import ThorlabsPM100, usbtmc
import pyvisa as visa
import os
import platform
from time import sleep


class PowerMeter:
    def __init__(self):

        os.system("cls" if os.name == "nt" else "clear")

        youros = platform.system()
        if youros == "Linux":
            print("You're running Linux")
            """
            The following line is the inst(rument) setup for linx
            """
            inst = usbtmc.USBTMC()  # device='/dev/usbtmc0'
        elif youros == "Windows":
            print("---")
            print("You're running Windows")
            """
            The following lines are the inst(rument) setup for linx windows
            """
            rm = visa.ResourceManager()
            # Trying a list of knwon Powermeter addresses
            pmlist = [
                "USB0::0x1313::0x8078::P0020110::INSTR",
                "USB0::0x1313::0x8079::P1001003::INSTR",
            ]

            print("---")
            connecting = True
            while connecting:
                for pm in pmlist:
                    try:
                        # timeout is in ms
                        inst = rm.open_resource(pm, timeout=1000)
                        print("Connected to: " + pm)
                        connecting = False
                        break
                    except:
                        print(pm + "  not found")
                        print("Available USB devices are:\n")
                        print(rm.list_resources())
            print("---")
        else:
            print("You are runnig an unknown system.")

        self.instr = ThorlabsPM100(inst=inst)
        sleep(1)
        self.instr.sense.power.dc.range.auto = "ON"

    def read(self):
        return self.instr.read
