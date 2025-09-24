#!/usr/bin/env python3
import sys
import os
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from . import nmea_sim
from pynmeagps import NMEAReader
import uart
import state
import time
import logging

gps_logger = logging.getLogger("gps")
gps_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

if not gps_logger.handlers:  # avoid duplicates if imported again
    fh = logging.FileHandler("./src/logs/gps.log", mode="w")
    fh.setFormatter(formatter)
    gps_logger.addHandler(fh)
    gps_logger.propagate = False

gps_logger.info("GPS log initialized")

#state.sim_on = True

def attemptParsing(msg):
    try:
        state.gps_lat = msg.lat
        state.gps_lon = msg.lon
        state.gps_alt = msg.alt
        state.gps_sats = msg.numSV
        gps_logger.info("%s,%s,%s,%s",state.gps_lat,state.gps_lon,state.gps_alt,state.gps_sats)
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
