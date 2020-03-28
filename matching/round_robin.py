import requests

import pandas as pd
import numpy as np
import re
from extra_functions import transform_trauma
import pandas as pd
from sklearn import preprocessing
import json
import pprint

def round_robin(user_zipcode, assignment, selected_hospitals):

    curr_location = get_user_lat_long(user_zipcode)
    # df = pd.read_csv('postprocess/Hospitals.csv')

    df = selected_hospitals


    ## TRAUMA and TYPE (https://www.amtrauma.org/page/traumalevels)
    df['MATCH_TRAUMA'] = df.apply(lambda row: get_match_trauma(assignment, row['TRAUMA']), axis=1)
    df['MATCH_TYPE'] = df.apply(lambda row: get_match_type(assignment, row['TYPE']), axis=1)
    df['MATCH'] = (df['MATCH_TRAUMA'] + df['MATCH_TYPE']).clip(0,1)

    ## DISTANCE
    df['DISTANCE'] = df.apply(lambda row: get_distance(curr_location, (row['X'], row['Y'])), axis=1)

    ## Weight Distance and Number of Beds (Scaled between 0 to 100)
    df['WEIGHTED_MATCH'] = df['MATCH'] * (0.2*df['BEDS'] - 0.8*df['DISTANCE'] + df['DISTANCE'].max())
    df['WEIGHTED_MATCH'] = df['WEIGHTED_MATCH'] / df['WEIGHTED_MATCH'].max() * 100


    ## SORT (Criteria = MATCH, LOCATION, NUMBER OF BEDS)
    # df.sort_values(by='WEIGHTED_MATCH', ascending = False, inplace=True)

    res = df[['NAME','ADDRESS','CITY','STATE','ZIP','TELEPHONE','TYPE','TRAUMA','DISTANCE', 'WEIGHTED_MATCH']].reset_index()

    print('User Location: ' + str(user_zipcode))
    print('User Assignment: ' + str(assignment))
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


# ## TEST CASES
# user_zipcode = 63112 # St.Louis
# assignment = ['Level 1','Pediatric','Children']
# round_robin(user_zipcode, assignment)



# user_zipcode = 98105 # Seattle
# assignment = ['Level 1','Pediatric','Children']
# round_robin(user_zipcode, assignment)







