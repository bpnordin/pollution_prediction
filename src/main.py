""" as primeagean said, I just have a main that only imports functions """
# getting the data from https://aqs.epa.gov/aqsweb/documents/data_api.html
import request_data
from loguru import logger
import pandas as pd
import time
import os

if __name__ == "__main__":
    # get a list of Parameters in a class
    # the class wer are using is "FORECAST"
    # the list can be seen at https://aqs.epa.gov/data/api/list/classes?email=test@aqs.api&key=test
    request_data.fetch_class_parameters()
