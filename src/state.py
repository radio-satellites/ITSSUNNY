#!/usr/bin/env python3 
#A place to hold all state files

import logging

#define states

BOOT = 0
IDLE = 1
GPS_WAIT_FIX = 2
TX_SSTV = 3
TX_APRS = 4

gps_lat = 0.0
gps_lon = 0.0
gps_alt = 0
gps_sats = 0

sim_on = False
sstv_on = False
aprs_on = False

aprs_packets = 0
aprs_period = 1

camera_period = 1

STATE = BOOT

callsign = ""

def changeState(newState): #QUick wrapper hee hee
    global STATE
    logging.info("Changing state from %s to %s",STATE,newState)
    STATE = newState