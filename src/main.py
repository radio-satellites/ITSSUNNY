#!/usr/bin/env python3
import logging
import yaml
import os
import state
import time
import threading

#Read config files before loading drivers


print("======ITSSUNNYMISSIONSOFTWARE======")
print("Written by VE3SVF with components ")
print("from other programs.")
print("==================================")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("./src/logs/mission.log", mode="w"),  # writes to file
        logging.StreamHandler()                        # prints to stdout
    ]
)
logging.info("Read config file...")
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.yaml")

# Load config from file
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

#is SITL running
if bool(config['simulation_on']):
    state.sim_on = True
    logging.warning("Simulation mode on! This should not be used for actual flights. ")

if bool(config['transmitter']['tx_sstv']):
    state.sstv_on = True

if bool(config['transmitter']['tx_aprs']):
    state.aprs_on = True

state.aprs_packets = int(config['aprs']['aprs_packets'])
state.aprs_period = int(config['aprs']['aprs_period'])
state.callsign = config['callsign']
state.camera_period = int(config['camera']['camera_period'])
logging.info("Config file OK.")

#Load drivers for gps, aprs and camera
from gps import fc_gps
from aprs import aprs
from camera import camera
from sstv import sstv

logging.info("Starting GPS reader...")
gps_thread = threading.Thread(target=fc_gps.mainloop)
gps_thread.start()

logging.info("Starting camera...")
camera_thread = threading.Thread(target=camera.mainloop)
camera_thread.start()

#Check for GPS Lock
state.changeState(state.GPS_WAIT_FIX)
logging.info("Waiting for GPS Lock...")
while (state.gps_sats == 0 or state.gps_alt == 0 or state.gps_lat == 0.0 or state.gps_lon == 0.0):
    #Do nothing
    time.sleep(5)
    logging.info("Waiting for GPS Lock...")
#Exiting means GPS has locked!
logging.info(
    "GPS has locked! Lat=%s Lon=%s Sats=%s Alt=%s",
    state.gps_lat, state.gps_lon, state.gps_sats, state.gps_alt
)
state.changeState(state.IDLE)
# start the main loop!
while True:
    for i in range(state.aprs_packets):
        #Send APRS packet
        logging.info("Sending APRS packet...")
        aprs.sendAPRS()
        time.sleep(state.aprs_period)
    #send SSTV
    sstv.run_encoding()
    sstv.send_sstv()