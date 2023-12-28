import json

base_string = "https://aqs.epa.gov/data/api/monitors/bySite?email=test@aqs.api&key=test&param=42401&bdate=20150501&edate=20150502&state=15&county=001&site=0007"

with open('config.json') as f:  # Replace with your file path
    config = json.load(f)

email = config['email']
key = config['key']

#TODO:
#make a config file
#place my values of email and key in it
#create the request url 
#fill values from each data frame row for the site
#get the params from https://aqs.epa.gov/data/api/list/parametersByClass?email=test@aqs.api&key=test&pc=FORECAST

