# Create Movies from Solar Dynamics Observatory Images
I have built a Sudden Ionospheric Disturbance receiver that can see the affects of solar activity on the D-layer of the ionosphere.
I have enjoyed correlating the VLF signal changes that I observe with movies of solar activity that NASA used to make available on their website: https://sdo.gsfc.nasa.gov/
That site has stopped being updated in September 2025 due to NASA budget cuts.

You can download images from the AIA instrument using the python package sunpy: https://docs.sunpy.org/en/stable/index.html
This yields a directory full of .fits files. To make a movie from them, the need to be converted to a more "normal" image format. The script, "convert_all_fits_to_pngs.py", will convert them into .png files.

I haven't made a script for the download of the .fits yet. I just followed the directions here: https://docs.sunpy.org/en/stable/tutorial/acquiring_data/jsoc.html

Then, you can use ffmpeg to turn those pngs into an mp4. The command that I used is:
```
ffmpeg -framerate 8 -i frame_%04d.png -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -pix_fmt yuv420p output_u16.mp4
```

I hope someone else might find this useful.
