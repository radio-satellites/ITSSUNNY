#!/usr/bin/env python3
"""
nmea_generator.py

Simple NMEA sentence generator. Produces commonly-used GPS sentences (GGA, RMC, GSA, GSV, GLL, VTG)
based on user-supplied parameters: latitude, longitude, altitude, number of satellites, fix quality,
speed (knots), course (degrees), hdop, and timestamp / date. Can run once or continuously at a given rate.
"""

import argparse
import datetime
import math
import random
import time
from typing import List, Tuple


def checksum(nmea: str) -> str:
    """Calculate NMEA sentence checksum (two hex digits) for the part between '$' and '*'"""
    cs = 0
    for ch in nmea:
        cs ^= ord(ch)
    return f"{cs:02X}"


def to_nmea_lat(lat: float) -> Tuple[str, str]:
    """Convert decimal degrees lat to NMEA ddmm.mmmm and hemisphere ('N'/'S')."""
    hemi = 'N' if lat >= 0 else 'S'
    lat_abs = abs(lat)
    degrees = int(lat_abs)
    minutes = (lat_abs - degrees) * 60.0
    # format ddmm.mmmm
    s = f"{degrees:02d}{minutes:07.4f}"
    return s, hemi


def to_nmea_lon(lon: float) -> Tuple[str, str]:
    """Convert decimal degrees lon to NMEA dddmm.mmmm and hemisphere ('E'/'W')."""
    hemi = 'E' if lon >= 0 else 'W'
    lon_abs = abs(lon)
    degrees = int(lon_abs)
    minutes = (lon_abs - degrees) * 60.0
    # format dddmm.mmmm
    s = f"{degrees:03d}{minutes:07.4f}"
    return s, hemi


def float_or_empty(value) -> str:
    """Return empty string if value is None, else formatted float without trailing zeros."""
    if value is None:
        return ''
    # Keep a reasonable number of decimals
    return f"{value:.1f}" if abs(value) >= 1.0 else f"{value:.2f}"


def make_sentence(talker: str, sentence_type: str, fields: List[str]) -> str:
    body = f"{talker}{sentence_type},{','.join(fields)}"
    cs = checksum(body)
    return f"${body}*{cs}"


def gga_sentence(lat: float, lon: float, alt: float, sats: int = 8, hdop: float = 0.9, fix_quality: int = 1, timestamp: datetime.datetime = None) -> str:
    """Generate GGA sentence (fix data).

    fields: UTC time, lat, N/S, lon, E/W, fix quality, num sats, HDOP, altitude (M), geoidal separation, (DGPS data)
    """
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()
    time_str = timestamp.strftime('%H%M%S.%f')[:-4]  # HHMMSS.ss (keep centiseconds)

    lat_s, lat_hemi = to_nmea_lat(lat)
    lon_s, lon_hemi = to_nmea_lon(lon)

    geoid_sep = ''  # unknown

    fields = [
        time_str,
        lat_s,
        lat_hemi,
        lon_s,
        lon_hemi,
        str(int(fix_quality)),
        f"{int(sats):02d}",
        f"{hdop:.1f}",
        f"{alt:.1f}",
        'M',
        geoid_sep,
        'M',
        '',
        ''
    ]
    return make_sentence('GP', 'GGA', fields)


def rmc_sentence(lat: float, lon: float, speed_knots: float = 0.0, course: float = 0.0, timestamp: datetime.datetime = None, magnetic_variation: float = None) -> str:
    """Recommended Minimum Specific GPS/Transit Data (RMC)

    fields: UTC time, status, lat, N/S, lon, E/W, speed (knots), course (degrees), date, mag var, mag var dir
    """
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()
    time_str = timestamp.strftime('%H%M%S.%f')[:-4]
    date_str = timestamp.strftime('%d%m%y')

    lat_s, lat_hemi = to_nmea_lat(lat)
    lon_s, lon_hemi = to_nmea_lon(lon)

    status = 'A'  # A = data valid

    mag = ''
    magdir = ''
    if magnetic_variation is not None:
        mag = f"{abs(magnetic_variation):.1f}"
        magdir = 'E' if magnetic_variation >= 0 else 'W'

    fields = [
        time_str,
        status,
        lat_s,
        lat_hemi,
        lon_s,
        lon_hemi,
        f"{speed_knots:.1f}",
        f"{course:.1f}",
        date_str,
        mag,
        magdir
    ]
    return make_sentence('GP', 'RMC', fields)


def vtg_sentence(speed_knots: float = 0.0, speed_kph: float = None, course: float = 0.0) -> str:
    """Course over ground and ground speed (VTG)

    fields: course, T, course magnetic, M, speed (knots), N, speed (km/h), K
    """
    if speed_kph is None:
        speed_kph = speed_knots * 1.852
    fields = [
        f"{course:.1f}",
        'T',
        '',
        'M',
        f"{speed_knots:.1f}",
        'N',
        f"{speed_kph:.1f}",
        'K'
    ]
    return make_sentence('GP', 'VTG', fields)


def gll_sentence(lat: float, lon: float, timestamp: datetime.datetime = None) -> str:
    """Geographic position - latitude/longitude (GLL)

    fields: lat, N/S, lon, E/W, UTC time, status, mode (optional)
    """
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()
    time_str = timestamp.strftime('%H%M%S.%f')[:-4]
    lat_s, lat_hemi = to_nmea_lat(lat)
    lon_s, lon_hemi = to_nmea_lon(lon)
    status = 'A'
    fields = [lat_s, lat_hemi, lon_s, lon_hemi, time_str, status]
    return make_sentence('GP', 'GLL', fields)


def gsa_sentence(sats_in_view: int = 8, pdop: float = 1.2, hdop: float = 0.9, vdop: float = 1.0, fix_mode: str = 'A', fix_type: int = 3) -> str:
    """DOP and active satellites (GSA)

    fix_mode: M = manual, A = automatic
    fix_type: 1 = no fix, 2 = 2D, 3 = 3D
    We will list up to 12 satellite PRNs (simulated) in the sentence.
    """
    prns = [str(1 + (i % 32)) for i in range(sats_in_view)]  # simulated PRNs 1..32
    # ensure 12 fields for PRNs
    prn_fields = prns[:12] + [''] * max(0, 12 - len(prns))
    fields = [fix_mode, str(fix_type)] + prn_fields + [f"{pdop:.1f}", f"{hdop:.1f}", f"{vdop:.1f}"]
    return make_sentence('GP', 'GSA', fields)


def gsv_sentences(sats_in_view: int = 8) -> List[str]:
    """Satellites in view (GSV) - may require multiple sentences if > 4 satellites.

    Each sentence carries info for up to 4 satellites: PRN, elevation, azimuth, SNR
    We'll simulate simple values.
    """
    sentences = []
    total = sats_in_view
    sentences_needed = (total + 3) // 4
    prn_base = 1
    for i in range(sentences_needed):
        chunk = list(range(prn_base + i * 4, min(prn_base + (i + 1) * 4, prn_base + total)))
        # pad to 4
        chunk += [0] * (4 - len(chunk))
        fields = [str(sentences_needed), str(i + 1), str(total)]
        for prn in chunk:
            if prn == 0:
                # empty fields
                fields.extend(['', '', '', ''])
            else:
                elev = random.randint(5, 80)
                az = random.randint(0, 359)
                snr = random.randint(20, 40)
                fields.extend([str(prn), str(elev), str(az), str(snr)])
        sentences.append(make_sentence('GP', 'GSV', fields))
    return sentences


def build_all_sentences(lat: float, lon: float, alt: float, sats: int = 8, speed_knots: float = 0.0, course: float = 0.0, hdop: float = 0.9, fix_quality: int = 1, timestamp: datetime.datetime = None) -> List[str]:
    ts = timestamp or datetime.datetime.utcnow()
    s = []
    s.append(gga_sentence(lat, lon, alt, sats=sats, hdop=hdop, fix_quality=fix_quality, timestamp=ts))
    s.append(rmc_sentence(lat, lon, speed_knots=speed_knots, course=course, timestamp=ts))
    s.append(vtg_sentence(speed_knots=speed_knots, course=course))
    s.append(gll_sentence(lat, lon, timestamp=ts))
    s.append(gsa_sentence(sats_in_view=sats, hdop=hdop, fix_type=3 if fix_quality >= 1 else 1))
    s.extend(gsv_sentences(sats_in_view=sats))
    return s


def demo_path(t0: datetime.datetime, t: float) -> Tuple[float, float]:
    """Generate a little circular walking path for demo mode; t is seconds since start."""
    # center Toronto-ish if no coords provided
    center_lat = 43.6532
    center_lon = -79.3832
    radius_deg = 0.0015  # ~167m
    angle = (t / 60.0) * 2 * math.pi  # one revolution every 60s
    lat = center_lat + radius_deg * math.cos(angle)
    lon = center_lon + radius_deg * math.sin(angle)
    return lat, lon


def returnGPS():

    if True: #In case you're wondering about this line - don't ask.
        start = time.time()
        rate = 1.0
        try:
            while True:
                t = time.time() - start
                lat, lon = demo_path(datetime.datetime.utcnow(), t)
                ts = datetime.datetime.utcnow()
                sentences = build_all_sentences(lat, lon, 100, sats=8, speed_knots=0, course=270, hdop=1.1, fix_quality=1, timestamp=ts)
                return '\r\n'.join(sentences)
        except KeyboardInterrupt:
            return


if __name__ == '__main__':
    returnGPS()
