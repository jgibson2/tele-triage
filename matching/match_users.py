import requests

import pandas as pd
import numpy as np
import re
import pandas as pd
from sklearn import preprocessing
import json
import pprint

from round_robin import round_robin
from extra_functions import convert_json_to_df




def get_matches(user_zipcode, assignment, selected_hospitals):
    df = convert_json_to_df(selected_hospitals)
    round_robin_results = round_robin(user_zipcode, assignment, df)

    res = list(round_robin_results['WEIGHTED_MATCH'])

    
    return res






## TEST CASES
# with open('Hospitals.geojson') as fp:
#     selected_hospitals = json.load(fp)
# user_zipcode = 63112 # St.Louis
# assignment = ['Level 1','Pediatric','Children']
# get_matches(user_zipcode, assignment, selected_hospitals)
