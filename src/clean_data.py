import numpy as np
from meteostat import Stations
import pandas as pd
import matplotlib as plt
from meteostat import Stations, Hourly


df = pd.read_csv("./data/pm2_2022_all_sites.csv")
df.sample(5)

# GPS location, I need to make sure that the sites I am getting data from are in the proper locations
# SITE_LATITUDE  SITE_LONGITUDE
#The Corners are bottom left 40.453217,-112.142944,top right: 40.809652,-111.818848

def detection_logic(SITE_LATITUDE: float, SITE_LONGITUDE: float) -> boolean:
    #only works because it is a rectangle and the sides are not at angles
    
    bottom_latitude = 40.453217
    top_latitude = 40.809652
    left_longitude = -112.142944
    right_longitude = -111.818848

    if (SITE_LATITUDE > bottom_latitude) & (SITE_LATITUDE < top_latitude):
        if (SITE_LONGITUDE < right_longitude) & (SITE_LONGITUDE > left_longitude):
            return True

    return False


filtered_df = df[df.apply(lambda row: detection_logic(row['SITE_LATITUDE'], row['SITE_LONGITUDE']), axis=1)]
filter_size = len(df) - len(filtered_df)
print(f"filtered out {filter_size} data points")


## weather station that are in the area we want
weather_df = pd.read_csv("data/isd-history.csv")

filtered_weather_df = weather_df[weather_df.apply(lambda row: detection_logic(row['LAT'], row['LON']), axis=1)]
filtered_weather_df.head()

filter_size = len(weather_df) - len(filtered_weather_df)
print(f"filtered out {filter_size} data points to a final size of {len(filtered_weather_df)}")
filtered_weather_df.head()

stations = Stations()
stations = stations.nearby(40.4532,-112)
stations = stations.fetch(20)

stations = stations[stations.apply(lambda row: detection_logic(row['latitude'], row['longitude']), axis=1)]

stations.head()

## Let 
