""" as primeagean said, I just have a main that only imports functions """
# getting the data from https://aqs.epa.gov/aqsweb/documents/data_api.html
import request_data
from loguru import logger
import pandas as pd

if __name__ == "__main__":
    # get a list of Parameters in a class
    # the class wer are using is "FORECAST"
    # the list can be seen at https://aqs.epa.gov/data/api/list/classes?email=test@aqs.api&key=test
    parameter_class = "FORECAST"
    parameter_list = request_data.get_pollutant_codes_from_class(parameter_class)
    logger.debug(f"\n{parameter_list}")
    sample_data = pd.DataFrame()
    for row in parameter_list.itertuples():
        logger.debug(f"Getting sample data for pollution {row.value_represented}")
        df = request_data.get_sample_data_by_box(row.code)
        logger.debug(f"\n{df}")
