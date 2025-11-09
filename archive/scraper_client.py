# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 06:16:28 2025

@author: markd

***************************** DEBUGGING SCRIPT  *****************************
Saved as an archive file to show a failed attempt to create a Scraper client in sunpy
This morphed into the scraper_download_files.py script

"""

from sunpy.net import Scraper
from sunpy.time import TimeRange

from datetime import datetime
import os
import re
import requests

# ENTER THESE VALUES FOR EACH DOWNLOAD

path_var = 'c:/Projects/aia_synoptic_downloads/'  # Directory to save .fits files to
start_time_utc = '2025-10-15T00:00:00'  # Time format YYYY-MM-DDThh:mm:ss
end_time_utc = '2025-10-15T23:59:59'
wvl = '0094'  # Usually, '0094' or '0131' for SIDs but there are other wavelengths too
time_step = 10 " Time_step in minutes between the images 

timerange = TimeRange(start_time_utc, end_time_utc)
date_str = start_time_utc.split('T')[0].replace('-', '')
OUTPUT_PATH = os.path.join(path_var, date_str, wvl)
os.makedirs(OUTPUT_PATH, exist_ok=True)


# Still haven't gotten the scraper client to work.
# from sunpy.net.dataretriever import GenericClient

# class MyAIAClient(GenericClient):
#     pattern = ('http://jsoc2.stanford.edu/data/aia/synoptic/{{year:4d}}/{{month:2d}}/{{day:2d}}/H{{hour:2d}}{{minute:2d}}/AIA{{year:4d}}{{month:2d}}{{day:2d}}_{{hour:2d}}{{minute:2d}}_0094.fits')

#     @classmethod
#     def register_values(cls):
#         from sunpy.net import attrs
#         adict = {attrs.Instrument: [('MyAIA', 'Atmospheric Imaging Assembly, which is part of the NASA Solar Dynamics Observatory mission.')],
#                 attrs.Physobs: [('intensity', 'intensity')],
#                 attrs.Source: [('SDO', 'The Solar Dynamics Observatory.')],
#                 attrs.Provider: [('JSOCSyn', 'Joint Science Operations Center Synoptic data')],
#                 attrs.Level: [('1.5', 'AIA synoptic data.')]}     
#         return adict
    
#     def search(self, *query):
#         # Create a Scraper instance with your pattern and instrument
#         scraper = Scraper(format=self.pattern, instrument='MyAIA')
        
#         # Use the Scraper to find files based on the query
#         # This will internally parse the time range from the query and match it against the pattern
#         return scraper._get_url_from_timerange(query[0]) # Assuming query[0] is the Time attribute


# This works for a scraper
pattern = ('http://jsoc2.stanford.edu/data/aia/synoptic/{{year:4d}}/{{month:2d}}/{{day:2d}}/H{{hour:2d}}00/AIA{{year:4d}}{{month:2d}}{{day:2d}}_{{hour:2d}}{{minute:2d}}_'+f'{wvl}.fits')

scraper = Scraper(format=pattern, Level=1)

scraper.range(timerange)
urls = scraper.filelist(timerange)

def select_every_ten_minutes(urls, delta_time):
    entries = []
    selected = []
    # Pattern: AIAYYYYMMDD_hhmm_<anydigits>.fits at the end of the URL
    pat = re.compile(r'AIA(\d{8})_(\d{4})_\d+.fits$')
    for url in urls:
        m = pat.search(url)
        if not m:
            continue
        yyyymmdd, hhmm = m.groups()
        dt = datetime.strptime(yyyymmdd + hhmm, "%Y%m%d%H%M")
        entries.append((dt, url))
    if not entries:
        print("No urls matched the pattern!")
        return []
    
    # Reference time (first file after sorting)
    t0 = entries[0][0]
    # Keep entries at 10-minute steps relative to t0
    delta_time_sec = delta_time * 60
    selected = [url for dt, url in entries if (dt - t0).total_seconds() % delta_time_sec == 0]
    return selected

selected_urls = select_every_ten_minutes(urls, time_step)

for url in selected_urls:
    filename = url.split('/')[-1] # Extract filename from URL
    output_file = os.path.join(OUTPUT_PATH, filename)
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Raise an exception for bad status codes
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {output_file}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
            