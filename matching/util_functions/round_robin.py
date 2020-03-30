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

# from extra_functions import get_distance
# from extra_functions import get_match_trauma
# from extra_functions import get_match_type
# from extra_functions import get_user_long_lat


def round_robin(user_zipcode, assignment, selected_hospitals, weights):
    df = selected_hospitals
    assignment = [el.lower() for el in assignment]
    curr_location = get_user_long_lat(user_zipcode)

    ## TRAUMA and TYPE (https://www.amtrauma.org/page/traumalevels)
    df['MATCH_TRAUMA'] = df.apply(lambda row: get_match_trauma(assignment, row['TRAUMA']), axis=1)
    df['MATCH_TYPE'] = df.apply(lambda row: get_match_type(assignment, row['TYPE']), axis=1)
    df['MATCH'] = (df['MATCH_TRAUMA'] + df['MATCH_TYPE']).clip(0, 1)

    ## DISTANCE
    df['DISTANCE'] = df.apply(
        lambda row: get_distance(curr_location, (row['LONGITUDE'], row['LATITUDE'])), axis=1)
    df['S_DISTANCE'] = (df['DISTANCE'] - df['DISTANCE'].min())/df['DISTANCE'].max()


    ## BEDS as an availability
    df['S_BEDS'] = (df.get('BEDS_AVAILABLE',0) / df['BEDS'])


    ## Weight Distance and Number of Beds (Scaled between 0 to 100)
    df['WEIGHTED_MATCH'] = df['MATCH'] * (
                weights['beds'] * df['BEDS'] + weights['beds_available'] * df['S_BEDS'] - weights['distance'] * df['S_DISTANCE'])
    df['WEIGHTED_MATCH'] = (df['WEIGHTED_MATCH']-df['WEIGHTED_MATCH'].min()) / (df['WEIGHTED_MATCH'].max()-df['WEIGHTED_MATCH'].min()) * 100

    # # ## If ventilator is non-negotiable
    if 'VENTILATORS' in df.columns:
        if 'ventilators' in assignment:
            df['WEIGHTED_MATCH'] = np.where(df['VENTILATORS'] == 0, 0, df['WEIGHTED_MATCH'])

    # # ## If testing kit is non-negotiable
    if 'TESTING_KITS' in df.columns:
        if 'kits' in assignment and 'ventilators' not in assignment:
            df['WEIGHTED_MATCH'] = np.where(df['TESTING_KITS'] == 0, 0, df['WEIGHTED_MATCH'])

    # # ## There must be providers available
    if 'PROVIDERS' in df.columns:
        df['WEIGHTED_MATCH'] = np.where(df['PROVIDERS'] < 10, 0, df['WEIGHTED_MATCH'])


    ## Rescale between 0 - 100
    df['WEIGHTED_MATCH'] = (df['WEIGHTED_MATCH']-df['WEIGHTED_MATCH'].min()) / (df['WEIGHTED_MATCH'].max()-df['WEIGHTED_MATCH'].min()) * 100

    ## SORT (Criteria = MATCH, LOCATION, NUMBER OF BEDS)
    # p =  df.sort_values(by='WEIGHTED_MATCH', ascending = False)
    # print(p.head(8))
    # p.to_csv('testoutput.csv',index=False)


    res = df[['NAME', 'ADDRESS', 'CITY', 'STATE', 'ZIP',
              'TELEPHONE', 'TYPE', 'TRAUMA', 'DISTANCE',
              'WEIGHTED_MATCH']].reset_index()

    # print('User Location: ' + str(user_zipcode))
    # print('User Assignment: ' + str(assignment))
    return res
