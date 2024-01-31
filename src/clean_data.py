import pandas as pd
import os
from loguru import logger
import datetime
import matplotlib.pyplot as plt
import subprocess

"""
need to determine inputs and outputs
and make a pandas dataframe with all the inputs and then all the correct outputs

inputs: 
61101	Wind Speed - Scalar
61102	Wind Direction - Scalar
61103	Wind Speed - Resultant
61104	Wind Direction - Resultant
62101	Outdoor Temperature
62103	Dew Point
62201	Relative Humidity 
63301	Solar radiation
64101	Barometric pressure
65102	Rain/melt precipitation
44201	Ozone
maybe these
42101	Carbon monoxide
42401	Sulfur dioxide
42402	Hydrogen sulfide
42600	Reactive oxides of nitrogen (NOy)
42601	Nitric oxide (NO)
42602	Nitrogen dioxide (NO2)
42603	Oxides of nitrogen (NOx)
42612	NOy - NO
43102	Total NMOC (non-methane organic compound)

Output:
44201	Ozone > but the next hour's ozone

Do it hour by hour or day by day? I like hour by hour, but that might be a lot 
harder, but the predictions might make a lot more sense
How far out can it predict? The output could be the Ozone for the next 24 hours

How do you incorporate multiple sites into this? There has got to be a way, 
but it would be more sophisticated
Just train it on each monitor site, then combine them in a fancy way

"""


def combine_sample_data(create_new_csv=True):
    data_directory = "data/sample_data/"
    filename = "full_df.csv"
    if not create_new_csv:
        return pd.read_csv(
            data_directory + filename, index_col=0, parse_dates=["datetime"]
        )

    paramater_list = [
        "61101",
        "61102",
        "61103",
        "61104",
        "62101",
        "62103",
        "62201",
        "63301",
        "64101",
        "65102",
        "44201",
    ]

    all_files_list = os.listdir(data_directory)
    data_files = [
        data_directory + file
        for file in all_files_list
        if os.path.splitext(file)[0] in paramater_list
    ]
    logger.opt(ansi=True).debug(
        f"<red>list of data files we are combingin into one pandas DF</>\n{data_files}"
    )

    prediction_dataframe = pd.DataFrame(
        columns=["latitude", "longitude", "datetime", "site_number"]
    )
    column_name_list = [
        "parameter",
        "latitude",
        "longitude",
        "date_local",
        "time_local",
        "sample_measurement",
        "site_number",
    ]
    for file in data_files:
        df = pd.read_csv(file, low_memory=False)
        if df.empty:
            logger.debug(f"{file} is empty")
            continue
        logger.debug(f"{file} is not empty")

        df = df[column_name_list]
        df = df.dropna()
        df = df.rename(columns={"sample_measurement": df.iloc[0]["parameter"]})
        df["datetime"] = pd.to_datetime(df["date_local"] + " " + df["time_local"])
        df = df.drop(["date_local", "time_local", "parameter"], axis=1)
        logger.debug(df.info())

        prediction_dataframe = prediction_dataframe.merge(
            df, on=["datetime", "latitude", "longitude", "site_number"], how="outer"
        )
    prediction_dataframe = prediction_dataframe.dropna()
    prediction_dataframe = add_previous_hour_ozone(prediction_dataframe)
    prediction_dataframe = fix_datetime(prediction_dataframe)
    prediction_dataframe.to_csv(data_directory + filename)
    return prediction_dataframe


def add_previous_hour_ozone(df):
    # per site number, go to the previous hour and find the ozone reading
    df = df.sort_values(by=["site_number", "datetime"])
    df["previous_hour_ozone"] = (
        df.groupby("site_number")["Ozone"].shift(1).fillna(df["Ozone"])
    )
    # make the 2022-01-01 00:00:00 just the same as the ozone from that hour
    return df

def fix_datetime(df):
    df['Month'] = df['datetime'].apply(lambda date: date.month)
    df['Day'] = df['datetime'].apply(lambda date: date.day)
    df['Hour'] = df['datetime'].apply(lambda date: date.hour)
    df['Week Day'] = df['datetime'].apply(lambda date: date.weekday())
    return df

if __name__ == "__main__":
    prediction_dataframe = combine_sample_data(create_new_csv=True)
    print(prediction_dataframe.head())
    print(prediction_dataframe.info())
    prediction_dataframe.hist(bins=50, figsize=(36, 24))
    plt.savefig("/tmp/plot.png")
    subprocess.run(["kitty", "icat", "/tmp/plot.png"])
