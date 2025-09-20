#!/usr/bin/env python3
import sys
import os
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from . import nmea_sim
from pynmeagps import NMEAReader
import uart
import state
import time

state.sim_on = True

def attemptParsing(msg):
    try:
        state.gps_lat = msg.lat
        state.gps_lon = msg.lon
        state.gps_alt = msg.alt
        state.gps_sats = msg.numSV
        #print("Got data!")
    except Exception as e:
        #print("Couldn't get data")
        x = 1 #Whatever

def mainloop():
    while True:
        data = ""
        if (state.sim_on):
            #Read from fake GPS
            data = nmea_sim.returnGPS()
            data = data.split("\r\n")
            for line in data:
                line = line + "\r\n"
                msg = NMEAReader.parse(line)
                attemptParsing(msg)
        else:
            data = ""
            #Read from other GPS (TODO)
        time.sleep(1)
        
#mainloop()
