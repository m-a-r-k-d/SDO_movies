# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 11:13:29 2025

*************************** DEBUGGING SCRIPT ******************************
Used to test conversion on a single .fits file

@author: markd
"""
import os
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.visualization import simple_norm
from PIL import Image, ImageDraw, ImageFont

INPUT_DIR = "c:/Projects/aia_downloads"       # Directory containing .fits/.fit files

# Load a fits file
f = os.path.join(INPUT_DIR, 'AIA20251015_000000_0094.fits') 
hdu_list = fits.open(f)
image_data = hdu_list[1].data
hdu_list.close()

# Create a ImageNormalize object. the asinh normalization looked good to me
norm_asinh = simple_norm(image_data, 'asinh', percent=99.25)
# Use the object to create normalized data
norm_data = norm_asinh(image_data)
norm_data_zeroed = norm_data - norm_data.min()
norm_data_final = norm_data_zeroed/norm_data_zeroed.max()
norm_data_u16 = (norm_data_final * 65535).astype(np.uint16)

plt.imshow(image_data, norm=norm_asinh, origin='lower', cmap='gray')
plt.axis('off')

# Add the date and time to the png
plt.text(0,5, "text for image", color= 'white')
# If you save with pyplot, you get an 8 bit png
# plt.savefig('c:/Projects/aia_downloads/pngs/asinh_AIA20251015_000000_0094.png', bbox_inches='tight', pad_inches=0)

img = Image.fromarray(norm_data_u16, mode='I;16') # 'I;16' for 16-bit grayscale
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("arial.ttf", size=30)
except IOError:
    font = ImageFont.load_default()
    print("Warning: arial.ttf not found, using default font.")
text_to_add = "Pillow Text Examplasdfasdfasdfe"
text_position = (10, 10)  # Adjust as needed
text_color = (65535,)
draw.text(text_position, text_to_add, font=font, fill=text_color)


img.save('c:/Projects/aia_downloads/pngs/asinh_16bit_output_image_text2.png')
