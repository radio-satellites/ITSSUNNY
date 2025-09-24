#This file handles capturing images automatically from cameras
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import state
from os import listdir
from os.path import isfile, join
import random
import time
import shutil

state.sim_on=True #COMMENT OUT AFTER DEVELOPMENT!

camera_logger = logging.getLogger("camera")
camera_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

if not camera_logger.handlers:  # avoid duplicates if imported again
    fh = logging.FileHandler("./src/logs/camera.log", mode="w")
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


script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "recover_index.txt")

img_path = os.path.join(script_dir, "images")
fake_img_path = os.path.join(img_path,"fake")

camera_index = int(open(config_path).read().strip())
camera_logger.info("Camera index is %s",camera_index)

def update_index(new_value):
    with open(config_path, "w") as f:
        f.write(str(int(new_value)))


def mainloop():
    global camera_index
    while True:
        # Take an image, save it, then wait
        if use_camera_driver:
            # cam.take_photo()
            x = 1  # Placeholder for real camera code
        else:
            # Use fake camera driver
            files_fake = [f for f in listdir(fake_img_path) if isfile(join(fake_img_path, f))]
            if not files_fake:
                camera_logger.warning("No fake images found in %s", fake_img_path)
                time.sleep(state.camera_period)
                continue

            image = random.choice(files_fake)
            camera_logger.info("Fake camera driver captured image: %s with index %s", image, camera_index)

            # Correct path handling
            fake_img_path_file = os.path.join(fake_img_path, image)
            dest_file = os.path.join(img_path, f"{camera_index}.jpg")

            # Copy the file
            shutil.copy(fake_img_path_file, dest_file)
        
        #advance index

        camera_index += 1
        update_index(camera_index)

        time.sleep(state.camera_period)

#mainloop()
