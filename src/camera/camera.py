#This file handles capturing images automatically from cameras
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import state

state.sim_on=True #COMMENT OUT AFTER DEVELOPMENT!

camera_logger = logging.getLogger("camera")
camera_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

if not camera_logger.handlers:  # avoid duplicates if imported again
    fh = logging.FileHandler("./logs/camera.log", mode="w")
    fh.setFormatter(formatter)
    camera_logger.addHandler(fh)
    camera_logger.propagate = False

camera_logger.info("Camera log initialized")


use_camera_driver = False
if not state.sim_on:
    from picamzero import Camera
    cam = Camera()
    #We initialized the camera, use the real driver
    use_camera_driver = True
    camera_logger.info("Using picamera driver...")
else:
    camera_logger.warning("Using virtual camera driver...")

def mainloop():
    while True:
        #Take an image, save it, then wait
        if use_camera_driver:
            