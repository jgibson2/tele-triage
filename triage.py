import requests
import numpy as np

from geolocation import GeoLocation
from matching.util_functions.extra_functions import get_user_long_lat


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

'''
Get zip codes in a certain radius (in km) around another zip code
'''
def get_zip_codes_in_radius(zip_code, radius, api_key):
    url = f'https://www.zipcodeapi.com/rest/{api_key}/radius.json/{zip_code}/{radius}/km'
    r = requests.get(url)
    if r:
        return [z['zip_code'] for z in r.json()['zip_codes']]
    else:
        raise ValueError(f"Could not complete request! Responded with code {r.status_code}")

'''
Get hospital service area data for zip codes
'''
def get_hospital_records_in_zip_codes(all_zip_codes):
    url = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Hospitals_1/FeatureServer/0/query'
    results = []
    for zip_codes in chunker(all_zip_codes, 25):
        zip_codes_string = ",".join(["'{}'".format(z) for z in zip_codes])
        params = {'where' : f'ZIP in({zip_codes_string})',
                  'f' : 'json',
                  'outFields': '*',
                  'returnGeometry': 'false'}

        r = requests.get(url, params=params)
        if r:
            results.extend(r.json()['features'])
        else:
            raise ValueError(f"Could not complete request! Responded with code {r.status_code}")
    return results


'''
Get hospitals within distance of zip code
'''
def get_hospital_records_within_distance(zip_code, distance_in_kilometers):
    url = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Hospitals_1/FeatureServer/0/query'
    lon, lat = get_user_long_lat(zip_code)
    loc = GeoLocation.from_degrees(lat, lon)
    SW_loc, NE_loc = loc.bounding_locations(distance_in_kilometers)
    params = {'where' : f'(LATITUDE BETWEEN {SW_loc.deg_lat} AND {NE_loc.deg_lat}) AND (LONGITUDE BETWEEN {SW_loc.deg_lon} AND {NE_loc.deg_lon})',
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
def make_hospital_choice(hospitals, weights=None, N=3):
    if weights is None:
        weights = [max(h['attributes']['BEDS'], 0) for h in hospitals]
    else:
        weights = weights + np.abs(np.minimum(np.min(weights), 0))
    weights = np.array(weights) / np.sum(weights)
    try:
        idxs = np.random.choice(list(range(len(hospitals))), N, p=weights, replace=False)
    except:
        idxs = list(range(len(hospitals)))
    wh = [(weights[idx], hospitals[idx]) for idx in idxs]
    return [h for w,h in sorted(wh, key=lambda x: x[0])]

