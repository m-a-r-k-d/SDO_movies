# -*- coding: utf-8 -*-
"""
Created on Sat Oct 18 14:17:15 2025

***************************** DEBUGGING SCRIPT  *****************************
Used to play with reading in .fits files

@author: markd
"""

import os
from astropy.io import fits
from PIL import Image
import numpy as np

with fits.open('AIA20251015_000000_0094.fits') as hdul:
    print(type(hdul))          # <class 'astropy.io.fits.hdu.hdulist.HDUList'>
    print(len(hdul))           # number of HDUs
    data0 = hdul[0].data         # primary HDU data
    print(getattr(data0, 'shape', None))
    data1 = hdul[1].data
    print(getattr(data1, 'shape', None))
    
def _load_fits_as_2d(path):
    """Load FITS data and return a 2D numpy array suitable for PNG conversion."""
    with fits.open(path) as hdul:
        data = hdul[0].data
        if data is None:
            data = hdul[1].data
        if data is None:
            raise ValueError(f"No image data found in FITS file: {path}")

    # If 3D, take the first plane
    if data.ndim == 3:
        data = data[0]

    # If still not 2D, try to squeeze
    if data.ndim != 2:
        data = np.squeeze(data)
        if data.ndim != 2:
            raise ValueError(f"Unsupported FITS data dimensions: {data.shape}")

    return np.asarray(data, dtype=np.float32)

def _normalize_to_uint8(data, vmin=None, vmax=None, method="minmax",
                      pmin=2.0, pmax=98.0, log_scale=False):
    """Normalize a 2D array to the 0-255 uint8 range for PNG output."""
    if log_scale:
        # Ensure positive values for log
        data = np.where(data > 0, data, 0)
        data = np.log10(data, where=data > 0, out=np.zeros_like(data))
        data[data < -15] = -15  # clamp extreme negatives for stability

        # Update vmin/vmax if not provided
        if vmin is None:
            vmin = np.min(data)
        if vmax is None:
            vmax = np.max(data)

    if vmin is None or vmax is None:
        if method == "percentile":
            if vmin is None:
                vmin = np.percentile(data, pmin)
            if vmax is None:
                vmax = np.percentile(data, pmax)
        else:
            vmin = np.min(data)
            vmax = np.max(data)

    if vmax <= vmin:
        # Degenerate case; create a zero image
        norm = np.zeros_like(data, dtype=np.float32)
    else:
        norm = (data - vmin) / (vmax - vmin)
        norm = np.clip(norm, 0.0, 1.0)

    # Map to 0-255
    img = (norm * 255.0).astype(np.uint8)
    return img