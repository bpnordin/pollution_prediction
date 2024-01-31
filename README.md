# pollution_prediction
Use weather data and pollution data to predict pollution levels in a very specific region

## scope
- I will use data for the the pollutants that go into the AQI
- The location will be the Wasatch front in Utah here ![here](https://github.com/bpnordin/pollution_prediction/blob/main/area_map.png)
- I need to determine exactly what my goal of prediction is


## small steps
- [ ] create requests to the epa database for the following infor
    - [ ] sites in a GPS bounding box
    - [ ] retrieve the parameter codes that are sent to Airnow (FORECAST)
    - [ ] 

## notes
While gathering information on pollution prediction here in the United States, I 
found out that the pollution data from https://aqs.epa.gov has basically everything
I need. 

Under the documentation https://aqs.epa.gov/aqsweb/documents/data_api.html here
are interesting things I found:
- You can get requests certain information, documentation here: https://aqs.epa.gov/aqsweb/documents/data_api.html#list
    - One interesting list is from the URL https://aqs.epa.gov/data/api/list/classes?email=test@aqs.api&key=test
    this shows you all the different collection sof parameters
    - to then get the POC for say forecaset you use https://aqs.epa.gov/data/api/list/parametersByClass?email=test@aqs.api&key=test&pc=FORECAST
- you can also request data by GPS bounding box, like I originally did, using 
&minlat=33.3&maxlat=33.6&minlon=-87.0&maxlon=-86.7 in the request URL (from the example)

I just need to use the sample data API https://aqs.epa.gov/aqsweb/documents/data_api.html#sample
to get the params from the FORECAST group by bounding box

After that, I will have to take a look at the data and move forward with some prediction 
stuff. 

There is also a python package, but it is not something that I need https://github.com/USEPA/pyaqsapi

For some reason it doesn't look like there is any weather data from doing the samepleData/byBox API.
I wonder if I will have to get that weather specifically by the region or something

And another thing, I have been playing with rust and I really like the way that the errors
bubble up as a part of the language itself, not something that I have to design. 
After writing the code to fetch the data from the API, I feel like I would have liked 
writing that code in rust very much. I think in the future I will re-write it in rust
and put the data in an SQL database that I can use python to analyze.
