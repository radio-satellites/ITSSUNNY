import logging
import os
import subprocess
from pathlib import Path
import state
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True  # allow Pillow to load truncated images
import time


sstv_logger = logging.getLogger("sstv")
sstv_logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

if not sstv_logger.handlers:  # avoid duplicates if imported again
    fh = logging.FileHandler("./src/logs/sstv.log", mode="w")
    fh.setFormatter(formatter)
    sstv_logger.addHandler(fh)
    sstv_logger.propagate = False

sstv_logger.info("SSTV log initialized")


def run_encoding():
    # Paths
    script_dir = Path(__file__).resolve().parent
    image_dir = script_dir.parent / "camera" / "images"
    sstv_dir = script_dir / "images"
    sstv_dir.mkdir(parents=True, exist_ok=True)

    # Get all images sorted by modification time (newest first)
    images = sorted(image_dir.glob("*.*"), key=os.path.getmtime, reverse=True)
    if not images:
        sstv_logger.warning("No images found in %s", image_dir)
        return

    # Take the last 5 chronologically
    last_five = images[:5]

    # Pick the largest one
    target_img = max(last_five, key=lambda f: f.stat().st_size)
    sstv_logger.info("Selected image: %s", target_img.name)

        # Copy to sstv/images
    copied_img = sstv_dir / target_img.name
    shutil.copy(target_img, copied_img)
    sstv_logger.debug("Copied image to %s", copied_img)

    # Load image
    img = Image.open(copied_img).convert("RGB")
    #resize to 640x496 for PD120
    img.thumbnail((640,492),Image.Resampling.LANCZOS)
    w, h = img.size

    # Add black bar at top
    bar_height = int(h * 0.12)  # keep some room
    new_img = Image.new("RGB", (w, h + bar_height), "black")
    new_img.paste(img, (0, bar_height))  # shift original image down

    # Overlay text (callsign, HAB, GPS)
    text = f"{state.callsign} HIGH ALTITUDE BALLOON"
    text2 = f"LAT:{state.gps_lat} LON:{state.gps_lon}"
    draw = ImageDraw.Draw(new_img)
    #print(script_dir)
    font_small = ImageFont.truetype(str(script_dir)+"/montserrat.ttf", 25)
    font_large = ImageFont.truetype(str(script_dir)+"/montserrat.ttf",28)

    draw.text(
        (15,0),
        text,
        fill="white",
        font=font_large
    )
    draw.text(
        (15,33),
        text2,
        fill="white",
        font=font_small
    )
    
    sstv_logger.debug("Annotated image with overlay: %s", text)

    # Save annotated image
    annotated_img = sstv_dir / f"annotated_{target_img.stem}.png"
    new_img.save(annotated_img, format="png")
    new_img.close()
    sstv_logger.info("Saved annotated image to %s", annotated_img)

    time.sleep(0.5)
    # Output WAV in script directory
    output_wav = script_dir / "output.wav"

    # Run pysstv in the background
    cmd = [
        "python", "-m", "pysstv",
        "--mode", "PD120",
        "--rate", "18000",
        "--vox",
        str(annotated_img),
        str(output_wav)
    ]

    subprocess.Popen(cmd, cwd=script_dir)
    sstv_logger.info("Running pysstv on %s, saving to %s", annotated_img.name, output_wav.name)

def send_sstv():

    subprocess.run(["aplay",str(Path(__file__).resolve().parent)+"/output.wav"])

#run_encoding()