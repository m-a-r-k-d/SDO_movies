# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 12:00:53 2025

************************** IN PRODUCTION  ************************************
This is the script that will convert a directory of .fits files to .png

Use ffmpeg to create movie from .pngs. This worked for me:
ffmpeg -framerate 8 -i frame_%04d.png -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -pix_fmt yuv420p output_u16.mp4



Converts .fits files with filenames AIAYYYYMMDD_HHMMSS_wavelength.fits to png files
Creates 16 bit .pngs

@author: markd
"""

import os
import re
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.visualization import simple_norm
import datetime as dt
from PIL import  Image, ImageDraw, ImageFont

INPUT_DIR = "c:/Projects/aia_downloads"       # Directory containing .fits/.fit files
OUTPUT_DIR = "c:/Projects/aia_downloads/pngs"     # Directory to write PNGs (frame_ naming is removed)

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

os.makedirs(OUTPUT_DIR, exist_ok=True)

fits_files = [
    os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR)
    if f.lower().endswith((".fits", ".fit"))
]
if not fits_files:
    print("No FITS files found.")

# Build an array of tuples. First element of tuple is the time stamp of the file.
# The second element of the tuple is the full path to the file. 
# Sort the tuples according to the date-time
fits_with_dt = [(extract_datetime_from_filename(p), p) for p in fits_files]
fits_with_dt.sort(key=lambda t: t[0])

# Use cnt for the filename of the output png
cnt = 0
for element in fits_with_dt:
    fits_path = element[1]
    base = os.path.basename(element[1])
    name_no_ext = os.path.splitext(base)[0]  # drop .fits/.fit
    name_list = name_no_ext.split('_')
    date_time = ' '.join(name_list[0:2])
    
    pad_cnt = f"{cnt:04d}"
    
    # ffmpeg requires a simple name for the .png like frame_xxxx.png
    output_path = os.path.join(OUTPUT_DIR, f"frame_{pad_cnt}.png")
    
    print(f"Converting {base}  -->  frame_{pad_cnt}.png")
    hdu_list = fits.open(fits_path)
    image_data = hdu_list[1].data
    hdu_list.close()
    
    # Create a ImageNormalize object. the asinh normalization looked good to me
    norm_asinh = simple_norm(image_data, 'asinh', percent=99.25)
    # Use the object to create normalized data
    norm_data = norm_asinh(image_data)
    norm_data_zeroed = norm_data - norm_data.min()
    norm_data_final = norm_data_zeroed/norm_data_zeroed.max()
    norm_data_u16 = (norm_data_final * 65535).astype(np.uint16)
    

    # Doing this with matplotlibs pyplot results in an 8 bit png
    # plt.imshow(norm_data_u16, norm=norm_asinh, origin='lower', cmap='gray')
    # plt.text(0, 10, date_time, color= 'white')
    # plt.axis('off')
    # plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    
    # Using Pillow, you can make a 16 bit png. Noticeably better movies.
    img = Image.fromarray(norm_data_u16, mode='I;16')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=30)
    except IOError:
        font = ImageFont.load_default()
        print("Warning: arial.ttf not found, using default font.")
    text_to_add = date_time
    text_position = (10, 10)  # Adjust as needed
    text_color = (65535,)  # White, single element tuple
    draw.text(text_position, text_to_add, font=font, fill=text_color)
    img.save(output_path)
    
    plt.close()
    cnt += 1
    

    
