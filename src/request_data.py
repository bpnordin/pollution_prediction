import json
import urllib.parse
import requests
import pandas as pd
from loguru import logger
import time


def build_url(base_path: str, params={}, config_file="config.json") -> str:
    """build out the URL for the AQS API"""
    with open(config_file) as f:  # Replace with your file path
        config = json.load(f)

    url_params = {"email": config["email"], "key": config["key"], **params}
    url_for_request = base_path + urllib.parse.urlencode(url_params)
    logger.debug(f"The URL for API request is:\n{url_for_request}")

    return url_for_request


def request_api(url: str, max_retries: int = 2, timeout=10) -> dict:
    """get the data from the API using the url
    the timeout is set at 3 because it takes like 100 seconds
    otherwise
    #TODO: add header option
        add more checks for data integrity response
    """

    data = None
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(url, timeout=timeout)
            data = response.json()
            logger.debug(
                f"The time elapsed of the api request is: {response.elapsed.total_seconds()}"
            )
            logger.debug(f"The response header is:\n{data['Header']}")
            if data["Header"][0]["status"] != "Success":
                return None
            return data

        except requests.exceptions.Timeout:
            timeout *= 2
            logger.debug(
                f"Timeout error occurred (retry {retries + 1}/{max_retries}) with new timeout {timeout} seconds"
            )
            retries += 1
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


def get_sample_data_by_box(
    pollutant_code: str, gps_box={}, timeout=100, max_retries=3
) -> pd.DataFrame:
    """
    this will get the monitors in the GPS region that have data corresponding
    to the code that we provide
    """
    url_byBox = "https://aqs.epa.gov/data/api/sampleData/byBox?"
    if gps_box == {}:
        gps_box = {
            "bottom_latitude": "40.453217",
            "top_latitude": "40.809652",
            "left_longitude": "-112.142944",
            "right_longitude": "-111.818848",
        }

    url = build_url(
        url_byBox,
        params={
            "param": pollutant_code,
            "bdate": "20220101",
            "edate": "20221231",
            "minlat": gps_box["bottom_latitude"],
            "maxlat": gps_box["top_latitude"],
            "minlon": gps_box["left_longitude"],
            "maxlon": gps_box["right_longitude"],
        },
    )
    response_dict = request_api(url, timeout=None, max_retries=max_retries)

    if response_dict:
        df = pd.DataFrame.from_dict(response_dict["Data"])
        return df

    logger.debug("No data retrieved from API")
    return pd.DataFrame()
