import pandas as pd
import os
from loguru import logger


def combine_csv_in_directory(data_directory: str):

    data_directory = "data/requested_data/"
    all_files_list = os.listdir(data_directory)
    logger.opt(ansi=True).debug(
        f"<red>list of data files we are combingin into one pandas DF</>\n{all_files_list}"
    )
   
    #some things about the data:
    #there are files that are empty
    #there are missing measurements
    #there are different sample frequencies
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
    for file in all_files_list:
        df = pd.read_csv(file, low_memory=False)
        if df.empty:
            logger.debug(f"{file} is empty")
            continue
        logger.debug(f"{file} is not empty")

        df = df[column_name_list]
        df = df.dropna()
        #make the sample measurement a unique column
        df = df.rename(columns={"sample_measurement": df.iloc[0]["parameter"]})
        df["datetime"] = pd.to_datetime(df["date_local"] + " " + df["time_local"])
        df = df.drop(["date_local", "time_local", "parameter"], axis=1)

        prediction_dataframe = prediction_dataframe.merge(
            df, on=["datetime", "latitude", "longitude", "site_number"], how="outer"
        )
    prediction_dataframe = prediction_dataframe.dropna()
    prediction_dataframe = add_previous_hour_ozone(prediction_dataframe)
    prediction_dataframe = add_datetime_categories(prediction_dataframe)
    return prediction_dataframe



def add_previous_hour_ozone(df):
    # per site number, go to the previous hour and find the ozone reading
    df = df.sort_values(by=["site_number", "datetime"])
    df["previous_hour_ozone"] = (
        df.groupby("site_number")["Ozone"].shift(1).fillna(df["Ozone"])
    )
    # make the 2022-01-01 00:00:00 just the same as the ozone from that hour
    return df


def add_datetime_categories(df):
    df["Month"] = df["datetime"].apply(lambda date: date.month)
    df["Day"] = df["datetime"].apply(lambda date: date.day)
    df["Hour"] = df["datetime"].apply(lambda date: date.hour)
    df["Week Day"] = df["datetime"].apply(lambda date: date.weekday())
    return df

