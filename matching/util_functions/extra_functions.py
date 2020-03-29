import pandas as pd
import numpy as np  
import json
import re
import requests





def transform_trauma(trauma):
    t = re.sub(r'[^A-Za-z0-9 ]+', '', trauma)
    res = re.sub(r'\b' + 'I' + r'\b', '1', t)
    res = re.sub(r'\b' + 'II' + r'\b', '2', res)
    res = re.sub(r'\b' + 'III' + r'\b', '3', res)
    res = re.sub(r'\b' + 'IV' + r'\b', '4', res)
    res = re.sub(r'\b' + 'V' + r'\b', '5', res)
    return res



def get_distance(curr_location, hospital_location):
    ## Haversine formula
    long1 = curr_location[0] * np.pi /180
    long2 = hospital_location[0] * np.pi /180

    lat1 = curr_location[1] * np.pi /180
    lat2 = hospital_location[1] * np.pi /180

    r = 6356.752

    inside_term = np.power(np.sin((lat2 - lat1)/2),2) + np.cos(lat1)*np.cos(lat2)*np.power(np.sin((long2-long1)/2),2)

    dist = 2 * r * np.arcsin((np.power(inside_term,0.5))) / 1.609 # in miles

    return dist

def get_match_trauma(assignment, trauma):
    if (trauma == 'NOT AVAILABLE'): return 1

    for criteria in assignment:
        if criteria.lower() in trauma.lower():
            return 1

    return 0

def get_match_type(assignment, visit_type):

    for criteria in assignment:
        if criteria.lower() in visit_type.lower():
            return 1
    return 0

def get_user_lat_long(user_zipcode):
    url = 'https://public.opendatasoft.com/api/records/1.0/search/?dataset=us-zip-code-latitude-and-longitude&q={user_zipcode}&facet=state&facet=timezone&facet=dst'.format(user_zipcode=user_zipcode)
    response = requests.get(url)
    
    res = response.json()
    latitude = res['records'][0]['fields']['latitude']
    longitude = res['records'][0]['fields']['longitude']
    return (longitude,latitude)


def convert_json_to_df(data):
    data = pd.io.json.json_normalize(data)

    df = pd.DataFrame(data)

    cols = list(df.columns)
    cols = [x.split('.')[1] for x in cols]
    df.columns = cols

    return df


