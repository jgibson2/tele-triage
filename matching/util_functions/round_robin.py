import requests
import pandas as pd
import numpy as np
import re
import pandas as pd
import json
import pprint

from matching.util_functions.extra_functions import get_distance
from matching.util_functions.extra_functions import get_match_trauma
from matching.util_functions.extra_functions import get_match_type
from matching.util_functions.extra_functions import get_user_long_lat


def round_robin(user_zipcode, assignment, selected_hospitals, weights):
    df = selected_hospitals
    curr_location = get_user_long_lat(user_zipcode)

    ## TRAUMA and TYPE (https://www.amtrauma.org/page/traumalevels)
    df['MATCH_TRAUMA'] = df.apply(lambda row: get_match_trauma(assignment, row['TRAUMA']), axis=1)
    df['MATCH_TYPE'] = df.apply(lambda row: get_match_type(assignment, row['TYPE']), axis=1)
    df['MATCH'] = (df['MATCH_TRAUMA'] + df['MATCH_TYPE']).clip(0, 1)

    ## DISTANCE
    df['DISTANCE'] = df.apply(
        lambda row: get_distance(curr_location, (row['LONGITUDE'], row['LATITUDE'])), axis=1)

    ## Weight Distance and Number of Beds (Scaled between 0 to 100)
    df['WEIGHTED_MATCH'] = df['MATCH'] * (
                weights['beds'] * df['BEDS'] - weights['distance'] * df['DISTANCE'] + df['DISTANCE'].max())
    df['WEIGHTED_MATCH'] = df['WEIGHTED_MATCH'] / df['WEIGHTED_MATCH'].max() * 100

    ## SORT (Criteria = MATCH, LOCATION, NUMBER OF BEDS)
    # df.sort_values(by='WEIGHTED_MATCH', ascending = False, inplace=True)

    res = df[['NAME', 'ADDRESS', 'CITY', 'STATE', 'ZIP',
              'TELEPHONE', 'TYPE', 'TRAUMA', 'DISTANCE',
              'WEIGHTED_MATCH']].reset_index()

    # print('User Location: ' + str(user_zipcode))
    # print('User Assignment: ' + str(assignment))
    return res
