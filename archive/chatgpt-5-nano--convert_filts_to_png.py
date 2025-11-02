# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 07:08:57 2025

@author: markd
"""

#!/usr/bin/env python3
"""
*************************** NOT IN PRODUCTION ****************************
I was debugging this, but found a better way!!!!!!!!!!!!!


Convert all FITS files in a directory to PNGs named after the FITS filename
(without the .fits extension). No command-line parsing; editable in IDE.

Test with your IDE by adjusting the constants below.
"""

import os
import re
import numpy as np
from astropy.io import fits
from PIL import Image
import datetime as dt

# ----------------- Editable test-time inputs -----------------
INPUT_DIR = "c:/Projects/aia_downloads"       # Directory containing .fits/.fit files
OUT_DIR   = "c:/Projects/aia_downloads/pngs"     # Directory to write PNGs (frame_ naming is removed)
METHOD    = "minmax"              # "minmax" or "percentile"
VMIN      = None
VMAX      = None
PMIN      = 2.0
PMAX      = 98.0
LOG_SCALE = False
WIDTH     = None                  # Optional resize width in pixels
HEIGHT    = None                  # Optional resize height in pixels
BIT_DEPTH = 16
# ---------------------------------------------------------------

def _load_fits_as_2d(path):
    with fits.open(path) as hdul:
        if len(hdul) != 2:
            raise ValueError(f"Unexpected number of Header Data Units in {path}.")
        data = hdul[0].data
        if data is None:
            data = hdul[1].data
        if data is None:
            raise ValueError(f"No data in this fits file, {path}")
    return np.asarray(data, dtype=np.float32)

def _normalize_to_uint8(data, vmin=None, vmax=None, method="minmax",
                      pmin=2.0, pmax=98.0, log_scale=False):
    if log_scale:
        data = np.where(data > 0, data, 0)
        data = np.log10(data, where=data > 0, out=np.zeros_like(data))
        data[data < -15] = -15
        if vmin is None:
            vmin = data.min()
        if vmax is None:
            vmax = data.max()

    if vmin is None or vmax is None:
        if method == "percentile":
            if vmin is None:
                vmin = np.percentile(data, pmin)
            if vmax is None:
                vmax = np.percentile(data, pmax)
        else:
            vmin, vmax = float(np.min(data)), float(np.max(data))

    if vmax <= vmin:
        norm = np.zeros_like(data, dtype=np.float32)
    else:
        norm = (data - vmin) / (vmax - vmin)
        norm = np.clip(norm, 0.0, 1.0)

    img = (norm * 255.0).astype(np.uint8)
    return img

def _normalize_to_uint16(data, vmin=None, vmax=None, method="minmax",
                       pmin=2.0, pmax=98.0, log_scale=False):
    """
    Normalize to 16-bit range (0-65535).
    Uses the same vmin/vmax logic as 8-bit version.
    """
    if log_scale:
        data = np.where(data > 0, data, 0)
        data = np.log10(data, where=data > 0, out=np.zeros_like(data))
        data[data < -15] = -15
        if vmin is None:
            vmin = data.min()
        if vmax is None:
            vmax = data.max()

    if vmin is None or vmax is None:
        if method == "percentile":
            if vmin is None:
                vmin = np.percentile(data, pmin)
            if vmax is None:
                vmax = np.percentile(data, pmax)
        else:
            vmin, vmax = float(np.min(data)), float(np.max(data))

    if vmax <= vmin:
        norm = np.zeros_like(data, dtype=np.float32)
    else:
        norm = (data - vmin) / (vmax - vmin)
        norm = np.clip(norm, 0.0, 1.0)

    img = (norm * 65535.0).astype(np.uint16)
    return img

def fits_to_png(input_path, output_path, method="minmax", vmin=None, vmax=None,
                pmin=2.0, pmax=98.0, log_scale=False,
                output_width=None, output_height=None, bit_depth=8):
    data = _load_fits_as_2d(input_path)

    if bit_depth == 16:
        img = _normalize_to_uint16(data, vmin=vmin, vmax=vmax, method=method,
                                 pmin=pmin, pmax=pmax, log_scale=log_scale)
        pil = Image.fromarray(img, mode="I;16")
    else:
        img = _normalize_to_uint8(data, vmin=vmin, vmax=vmax, method=method,
                                pmin=pmin, pmax=pmax, log_scale=log_scale)
        pil = Image.fromarray(img, mode="L")

    if output_width is not None or output_height is not None:
        new_w = output_width if output_width is not None else pil.width
        new_h = output_height if output_height is not None else pil.height
        pil = pil.resize((new_w, new_h), resample=Image.BILINEAR)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pil.save(output_path)
    return True

def extract_datetime_from_filename(filepath):
    base = os.path.basename(filepath)
    m = re.match(r'^AIA(\d{8})_(\d{6})', base)
    if not m:
        raise ValueError(
            f"Filename does not match the required pattern 'AIAYYYYMMDD_HHMMSS...': {base}"
        )
    dt_str = m.group(1) + m.group(2)  # YYYYMMDDHHMMSS
    try:
        return dt.datetime.strptime(dt_str, "%Y%m%d%H%M%S")
    except ValueError:
        raise ValueError(f"Filename pattern matched but invalid date/time: {base}")


# ----------------- Main (no CLI) -----------------
def main():
    in_dir = INPUT_DIR
    out_dir = OUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    fits_files = [
        os.path.join(in_dir, f) for f in os.listdir(in_dir)
        if f.lower().endswith((".fits", ".fit"))
    ]
    if not fits_files:
        print("No FITS files found.")
        return 1

    # Build and sort with strict date-time from filename
    fits_with_dt = [(extract_datetime_from_filename(p), p) for p in fits_files]
    fits_with_dt.sort(key=lambda t: t[0])

    for element in fits_with_dt:
        path = element[1]
        base = os.path.basename(element[1])
        name_no_ext = os.path.splitext(base)[0]  # drop .fits/.fit
        out_path = os.path.join(out_dir, f"{name_no_ext}.png")

        fits_to_png(
            input_path=path,
            output_path=out_path,
            method=METHOD,
            vmin=VMIN,
            vmax=VMAX,
            pmin=PMIN,
            pmax=PMAX,
            log_scale=LOG_SCALE,
            output_width=WIDTH,
            output_height=HEIGHT,
            bit_depth=BIT_DEPTH,
        )
        print(f"Wrote PNG: {out_path}")

    print("Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())