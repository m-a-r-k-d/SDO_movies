# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 07:13:09 2025

@author: markd
"""

import os
from astropy.io import fits
from astropy.visualization import simple_norm
from PIL import  Image
import numpy as np

date_str = '20250810'
wvl = '0094'
input_file = 'AIA20250810_0540_0094.fits'
stretch = 'asinh'
asinh_a = 0.7 # default = 0.1
# percent = 89.0
min_percent = 0.0
max_percent = 80.0
output_file = f'AIA20250810_0540_0094_{stretch}_{asinh_a}_{min_percent}_{max_percent}.png'

INPUT_DIR = os.path.join("c:/Projects/aia_synoptic_downloads", date_str, wvl)       # Directory containing .fits/.fit files
OUTPUT_DIR = os.path.join("c:/Projects/aia_synoptic_downloads",date_str, wvl, 'png')     # Directory to write PNGs
os.makedirs(OUTPUT_DIR, exist_ok=True)

fits_path =  os.path.join(INPUT_DIR, input_file)
output_path = os.path.join(OUTPUT_DIR, output_file)

hdu_list = fits.open(fits_path)
image_data = hdu_list[1].data
hdu_list.close()

# Create a ImageNormalize object. the asinh normalization looked good to me
norm_asinh = simple_norm(image_data, stretch, asinh_a=asinh_a, min_percent=min_percent, max_percent=max_percent)
# Use the object to create normalized data
norm_data = norm_asinh(image_data)
norm_data_zeroed = norm_data - norm_data.min()
norm_data_final = norm_data_zeroed/norm_data_zeroed.max()
norm_data_u16 = (norm_data_final * 65535).astype(np.uint16)

img = Image.fromarray(norm_data_u16, mode='I;16')
# draw = ImageDraw.Draw(img)

img.save(output_path)

# plt.close() # For matplotlib, close the plt object
img.close() # For Pillow, close the image