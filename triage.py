import requests
import numpy as np

'''
Get zip codes in a certain radius (in miles) around another zip code
'''
def get_zip_codes_in_radius(zip_code, radius, api_key):
    url = f'https://www.zipcodeapi.com/rest/{api_key}/radius.json/{zip_code}/{radius}/mile'
    r = requests.get(url)
    if r:
        return [z['zip_code'] for z in r.json()['zip_codes']]
    else:
        raise ValueError(f"Could not complete request! Responded with code {r.status_code}")

'''
Get hospital service area data for zip codes
'''
def get_hospital_records_in_zip_codes(zip_codes):
    url = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Hospitals_1/FeatureServer/0/query'
    zip_codes_string = ",".join(["'{}'".format(z) for z in zip_codes])
    params = {'where' : f'ZIP in({zip_codes_string})',
              'f' : 'json',
              'outFields': '*',
              'returnGeometry': 'false'}

    r = requests.get(url, params=params)
    if r:
        return r.json()['features']
    else:
        raise ValueError(f"Could not complete request! Responded with code {r.status_code}")

'''
Make a hospital choice based on number of beds, randomly chooses from the list

Input data from get_hospital_records_in_zip_codes (filtered for appropriate care level)
'''
def make_hospital_choice(hospitals, weights=None):
    if weights is None:
        weights = [h['attributes']['BEDS'] for h in hospitals]
    weights = np.array(weights) / np.sum(weights)
    return np.random.choice(hospitals, 1, p=weights)

