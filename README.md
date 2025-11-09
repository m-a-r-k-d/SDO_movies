# Create Movies from Solar Dynamics Observatory Images
I have built a Sudden Ionospheric Disturbance receiver that can see the affects of solar activity on the D-layer of the ionossphere.
I have enjoyed correlating the VLF signal changes that I observe with movies of solar activity that NASA used to make available on their website: https://sdo.gsfc.nasa.gov/
That site has stopped being updated in September 2025 due to NASA budget cuts.

You can download images from the AIA instrument using the python package sunpy: https://docs.sunpy.org/en/stable/index.html
This yields a directory full of .fits files. To make a movie from them, the need to be converted to a more "normal" image format. The script, "convert_all_fits_to_pngs.py", will convert them into .png files.

## About downloading files
The movies that I used to download seemed to be based on 1024x1024 data. The .fits that you can get via the Virtual Solar Observatory are "level one" data which seems to mean that they are 4096x4096. These files are ~64MB when downloaded, so they will take up a bunch of disk space.

I found that the "synoptic data" from the AIA instrument is lower resolution. It can be found here: http://jsoc2.stanford.edu/data/aia/synoptic/
Right now, 11-9-2025, the synoptic data is also not being updated - maybe due to the goverment shutdown? We'll see if it starts up again.

I use sunpy's Scraper function to get the synoptic data in 'scraper_download_files.py"

When I compare the movies these scripts make with the movies that I used to download - the ones NASA created are better. No surprise there, really. The solar flares in the NASA movies look more intense - i.e. they are brighter. Also, it seems like they have used some overall normalization from frame to frame because my movies show variation in the background intensity between the frames. I have played with the stretching that I use in the simple_norm function for a couple of hours, but I haven't really found something similar. 

## File conversion
The script convert_all_files_to_pngs.py now also makes the mp4 file. You will need to install ffmpeg and have it in your system's PATH variable. The package ffmpeg-python must also be installed. It's a Python wrapper for ffmpeg.  

Here is the command that I used to run from the command line:
```
ffmpeg -framerate 8 -i frame_%04d.png -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -pix_fmt yuv420p output_u16.mp4
```

## Archive directory
This directory of the repo containes files that I've used for debugging.

**I hope this helps someone else.
