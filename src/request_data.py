import json
import urllib.parse
import requests
import pandas as pd
from loguru import logger
import time
import os


def build_url(base_path: str, params={}, config_file="config.json") -> str:
    """this is a helper function that builds out the URL for the AQS API"""
    with open(config_file) as f:  # Replace with your file path
        config = json.load(f)

    url_params = {"email": config["email"], "key": config["key"], **params}
    url_for_request = base_path + urllib.parse.urlencode(url_params)
    logger.debug(f"The URL for API request is:\n{url_for_request}")

    return url_for_request


def request_api(url: str, max_retries: int = 2, timeout=100) -> dict:
    """Use python's request library to get the data from the AQS API using the url
    and return the request in the form of a python dictionary
    #TODO: add header option
        add more checks for data integrity response
    """

    data = None
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = requests.get(url, timeout=timeout)
            data = response.json()
            logger.debug(
                f"The time elapsed of the api request is: {response.elapsed.total_seconds()}"
            )
            logger.debug(f"The response header is:\n{data['Header']}")
            if data["Header"][0]["status"] != "Success":
                logger.warning(
                    "Returning empty dict. The request did not respond with a succcess"
                )
                return None
            return data

        except requests.exceptions.Timeout:
            timeout *= 2
            logger.debug(
                f"Timeout error occurred (retry {retry_count + 1}/{max_retries}) with new timeout {timeout} seconds"
            )
            retry_count += 1
            # sleep 5 seconds so we don't get rate limited
            time.sleep(5)

    logger.warning(
        f"Max number of retries of {max_retries} reached. Returning empty dict"
    )
    return None


def get_pollutant_codes_from_class(parameter_class: str) -> pd.DataFrame:
    """this function takes a parameter class(group of parameters) string and
    gets a list of the pollutant codes that are from that class
    """
    url_class = "https://aqs.epa.gov/data/api/list/parametersByClass?"
    url = build_url(url_class, {"pc": parameter_class})
    response_dict = request_api(url)

    if response_dict:
        df = pd.DataFrame.from_dict(response_dict["Data"])
        return df
    return pd.DataFrame()


def fetch_data_by_box(
    pollutant_code: str,
    begin_date: str,
    end_date: str,
    gps_box: dict,
    max_retries=3,
) -> pd.DataFrame:
    """
    this will get the monitors in the GPS region that have data corresponding
    to the code that we provide
    """
    url_byBox = "https://aqs.epa.gov/data/api/sampleData/byBox?"
    url = build_url(
        url_byBox,
        params={
            "param": pollutant_code,
            "bdate": begin_date,
            "edate": end_date,
            "minlat": gps_box["bottom_latitude"],
            "maxlat": gps_box["top_latitude"],
            "minlon": gps_box["left_longitude"],
            "maxlon": gps_box["right_longitude"],
        },
    )
    response_dict = request_api(url, timeout=None, max_retries=max_retries)
    #sleep so no rate limit
    time.sleep(5)

    if response_dict:
        df = pd.DataFrame.from_dict(response_dict["Data"])
        return df

    logger.debug("No data retrieved from API")
    return pd.DataFrame()


def fetch_all_data(parameter_class, gps_box, begin_date, end_date):
    """
    This function fetch all the data from a given class and a given gps box
    and save it in a csv file
    if it is already in a csv file, it will not re-get the data
    (for now, just to save time with everything)
    I definitely need to re-engineer the data pipline lol"""

    parameter_list = get_pollutant_codes_from_class(parameter_class)
    logger.debug(f"\n{parameter_list}")

    if parameter_list.empty is False:

        for row in parameter_list.itertuples():
            logger.debug(f"Getting sample data for {row.value_represented}")
            file_name = f"data/requested_data/{row.code}_{begin_date}_{end_date}.csv"

            if os.path.exists(file_name):
                logger.debug("The data is already saved in file format")
            else:
                logger.debug("Fetching data through the API")
                df = fetch_data_by_box(row.code, begin_date, end_date, gps_box)
                df.to_csv(file_name)

    else:
        logger.warning(f"Could not get the parameter list {parameter_class}")
