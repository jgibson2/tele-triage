import requests
import pandas as pd
import numpy as np
import re
import pandas as pd
import json
import pprint
import sys
import random

from matching.util_functions.round_robin import round_robin
from matching.util_functions.extra_functions import convert_json_to_df

# sys.path.insert(0,'./util_functions/')
# from round_robin import round_robin
# from extra_functions import convert_json_to_df
# sys.path.insert(0,'../test_assets/')
# import test_assets

def get_match_weights(user_zipcode, assignment, selected_hospitals, weights={'beds':0.2, 'beds_available': 10,'distance':0.8,'level': 1}):
    df = convert_json_to_df(selected_hospitals)
    round_robin_results = round_robin(user_zipcode, assignment, df, weights)
    res = list(round_robin_results['WEIGHTED_MATCH'])
    return res


## Testing
def test_match_users():
    # selected_hospitals = test_assets.test_hospitals
    # for i in range(len(selected_hospitals)):
    #     if selected_hospitals[i]['attributes']['BEDS'] <= 0:
    #         selected_hospitals[i]['attributes']['BEDS_AVAILABLE'] = 0
    #     else:
    #         selected_hospitals[i]['attributes']['BEDS_AVAILABLE'] = random.randrange(0, selected_hospitals[i]['attributes']['BEDS'])
    #     selected_hospitals[i]['attributes']['PROVIDERS'] = random.randrange(10,100) * random.randint(0,1)
    #     selected_hospitals[i]['attributes']['VENTILATORS'] = random.randrange(10,100) * random.randint(0,1)
    #     selected_hospitals[i]['attributes']['TESTING_KITS'] = random.randrange(10,100) * random.randint(0,1)

    ## Test 1
    user_zipcode = 44105 # St.Louis
    assignment = ['Level 1','Pediatric','Children', 'ventilator', 'kit']
    weights = {
        'beds':0.5,
        'beds_available': 10,
        'distance': 0.5,
    }
    get_match_weights(user_zipcode, assignment, selected_hospitals, weights)
    ## Test 2
    user_zipcode = 97035 # Portland, OR
    assignment = ['Level 2','Pediatric','Trauma','kit']
    weights = {
        'beds': 0.3,
        'beds_available': 5,
        'distance': 0.7,
    }
    get_match_weights(user_zipcode, assignment, selected_hospitals, weights)

    ## Test 3
    user_zipcode = 33125 # Miami, FL
    assignment = ['Level 1','Military','ventilator']
    get_match_weights(user_zipcode, assignment, selected_hospitals)