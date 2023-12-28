import numpy as np
from meteostat import Stations
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from meteostat import Stations, Hourly
import subprocess


df = pd.read_csv("./data/pm2_2022_all_sites.csv")
df.sample(5)

# GPS location, I need to make sure that the sites I am getting data from are in the proper locations
# SITE_LATITUDE  SITE_LONGITUDE
# The Corners are bottom left 40.453217,-112.142944,top right: 40.809652,-111.818848


def detection_logic(SITE_LATITUDE: float, SITE_LONGITUDE: float) -> bool:
    # only works because it is a rectangle and the sides are not at angles
    bottom_latitude: float = 40.453217
    top_latitude: float = 40.809652
    left_longitude: float = -112.142944
    right_longitude: float = -111.818848

    if (SITE_LATITUDE > bottom_latitude) & (SITE_LATITUDE < top_latitude):
        if (SITE_LONGITUDE < right_longitude) & (SITE_LONGITUDE > left_longitude):
            return True

    return False


filtered_pollution_df = df[
    df.apply(
        lambda row: detection_logic(row["SITE_LATITUDE"], row["SITE_LONGITUDE"]),
        axis=1,
    )
]
filter_size = len(df) - len(filtered_pollution_df)
print(f"filtered out {filter_size} data points")


# weather station that are in the area we want
weather_df = pd.read_csv("data/isd-history.csv")

filtered_weather_df = weather_df[
    weather_df.apply(lambda row: detection_logic(row["LAT"], row["LON"]), axis=1)
]

stations = Stations()
stations = stations.nearby(40.4532, -112)
stations = stations.fetch(20)

stations = stations[
    stations.apply(
        lambda row: detection_logic(row["latitude"], row["longitude"]), axis=1
    )
]


def display(fig):
    fig.savefig("/tmp/plot.png", pad_inches=0.1, bbox_inches="tight")
    subprocess.call(["kitty", "+kitten", "icat", "--align", "left", "/tmp/plot.png"])


# Let us just take a look at the year 2022 and play aroundn with it
start = datetime(2022, 1, 1)
end = datetime(2022, 12, 31, 23, 59)

data = Hourly(stations, start=start, end=end)
data = data.normalize()
data = data.fetch()
filtered_pollution_df.set_index("Date")
data = data.unstack(level=0)
fig, ax = plt.subplots(2, 2, figsize=(20, 20))
data.plot(y=("prcp", "72572"), ax=ax[0, 1])
data.plot(y=("prcp", "KU420"), ax=ax[0, 0])
display(fig)

fig, ax = plt.subplots()
filtered_pollution_df[filtered_pollution_df["Site Name"] == "Copper View"][
    "Daily Max 8-hour CO Concentration"
].plot()
display(fig)
