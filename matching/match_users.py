import requests
import pandas as pd
import numpy as np
import re
import pandas as pd
import json
import pprint
import sys
from sklearn import preprocessing
from matching.util_functions.round_robin import round_robin
from matching.util_functions.extra_functions import convert_json_to_df




def get_matches(user_zipcode, assignment, selected_hospitals, weights={'beds':0.2, 'distance':0.8,'level': 1}):
    df = convert_json_to_df(selected_hospitals)
    round_robin_results = round_robin(user_zipcode, assignment, df, weights)

    res = list(round_robin_results['WEIGHTED_MATCH'])
    print(res)
    return res


## Testing
def test_match_users():
    with open('original_data/Hospitals.geojson') as fp:
        selected_hospitals = json.load(fp)

    ## Test 1
    user_zipcode = 63112 # St.Louis
    assignment = ['Level 1','Pediatric','Children']
    weights = {
        'beds': 0.5,
        'distance': 0.5,
    }
    get_matches(user_zipcode, assignment, selected_hospitals, weights)

    ## Test 2
    user_zipcode = 97035 # Portland, OR
    assignment = ['Level 2','Pediatric','Trauma']
    weights = {
        'beds': 0.3,
        'distance': 0.7,
    }

    get_matches(user_zipcode, assignment, selected_hospitals, weights)

    ## Test 3
    user_zipcode = 33125 # Miami, FL
    assignment = ['Level 1','Military']
    get_matches(user_zipcode, assignment, selected_hospitals)
