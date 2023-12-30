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
    parameter_class = "FORECAST"
    parameter_list = request_data.get_pollutant_codes_from_class(parameter_class)
    logger.debug(parameter_list)

    if parameter_list.empty is False:
        logger.debug(f"\n{parameter_list}")
        sample_data = pd.DataFrame()
        for row in parameter_list.itertuples():
            logger.debug(f"Getting sample data for {row.value_represented}")
            file_name = f"data/sample_data/{row.code}.csv"
            if os.path.exists(file_name):
                df = pd.read_csv(file_name)
            else:
                df = request_data.get_sample_data_by_box(row.code)
                df.to_csv(file_name)

            if df.empty is False:
                # do stuff to data here
                pass
            logger.debug(f"\n{df}")
            time.sleep(5)
    else:
        logger.debug("Could not get the parameter list")
