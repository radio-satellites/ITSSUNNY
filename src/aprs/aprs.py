import os
import state
import subprocess
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "aprs_mod.py")
wav_path = os.path.join(script_dir, "aprs.wav")


from datetime import datetime

def aprs_position_packet(lat, lon, symbol_table='/', symbol='O', comment='', include_timestamp=True):
    """
    Build a simple APRS position packet, optionally with timestamp.
    
    lat, lon: decimal degrees (positive N/E, negative S/W)
    symbol_table: '/' = primary, '\' = alternate
    symbol: symbol code (e.g. '>' = car, 'O' = balloon)
    comment: free text after position
    include_timestamp: if True, prepends UTC timestamp in DDHHMMz format
    """

    # Get timestamp if requested
    timestamp_str = ''
    if include_timestamp:
        now = datetime.utcnow()
        timestamp_str = now.strftime("%d%H%Mz")  # DDHHMMz format

    # Latitude conversion
    lat_deg = int(abs(lat))
    lat_min = (abs(lat) - lat_deg) * 60
    lat_hem = 'N' if lat >= 0 else 'S'
    lat_str = f"{lat_deg:02d}{lat_min:05.2f}{lat_hem}"

    # Longitude conversion
    lon_deg = int(abs(lon))
    lon_min = (abs(lon) - lon_deg) * 60
    lon_hem = 'E' if lon >= 0 else 'W'
    lon_str = f"{lon_deg:03d}{lon_min:05.2f}{lon_hem}"

    # Assemble packet
    info_field = f"!{lat_str}{symbol_table}{lon_str}{symbol}{comment}" #replace with {timestamp_str} at the beginning
    return info_field

def sendAPRS():
    packet = aprs_position_packet(
        state.gps_lat,
        state.gps_lon,
        comment=str(state.gps_alt) + "m ASL"
    )
    full_frame = f"{state.callsign}>APRS:{packet}"
    #print("Generated APRS frame:", full_frame)

    # Run aprs_mod.py and feed the frame in via stdin
    subprocess.run(
        ["python", config_path, "-t", wav_path, "-t", "-"],
        input=full_frame.encode(),
        check=True
    )
    subprocess.run(["aplay", wav_path])