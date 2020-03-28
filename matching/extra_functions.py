import pandas as pd
import numpy as np  
import json
import re
from pandas.io.json import json_normalize





def transform_trauma(trauma):
    t = re.sub(r'[^A-Za-z0-9 ]+', '', trauma)
    res = re.sub(r'\b' + 'I' + r'\b', '1', t)
    res = re.sub(r'\b' + 'II' + r'\b', '2', res)
    res = re.sub(r'\b' + 'III' + r'\b', '3', res)
    res = re.sub(r'\b' + 'IV' + r'\b', '4', res)
    res = re.sub(r'\b' + 'V' + r'\b', '5', res)
    return res



def convert_json_to_df(data):
    data = data['features']
    data = json_normalize(data)

    df = pd.DataFrame(data)
    df.drop(['type'], axis=1, inplace=True)

    cols = list(df.columns)
    cols = [x.split('.')[1] for x in cols]
    df.columns = cols

    df['X'] = df['coordinates'].apply(lambda row: row[0])
    df['Y'] = df['coordinates'].apply(lambda row: row[1])
    df.drop(['type', 'coordinates','OBJECTID'], axis=1, inplace=True)


    return df

