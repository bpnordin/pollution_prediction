""" as primeagean said, I just have a main that only imports functions """
# getting the data from https://aqs.epa.gov/aqsweb/documents/data_api.html
import request_data

if __name__ == "__main__":
    # use python to get data from AQS API
    # the class wer are using is "FORECAST"
    # the list can be seen at https://aqs.epa.gov/data/api/list/classes?email=test@aqs.api&key=test
    forecast_class = "FORECAST"
    gps_box = {
        "bottom_latitude": "40.453217",
        "top_latitude": "40.809652",
        "left_longitude": "-112.142944",
        "right_longitude": "-111.818848",
    }
    begin_date = "20220101"
    end_date = "20221231"
    request_data.fetch_all_data(forecast_class, gps_box, begin_date, end_date)
