import requests
import numpy as np

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

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
Make a hospital choice based on number of beds, randomly chooses from the list

Input data from get_hospital_records_in_zip_codes (filtered for appropriate care level)
'''
def make_hospital_choice(hospitals, weights=None, N=3):
    if weights is None:
        weights = [max(h['attributes']['BEDS'], 0) for h in hospitals]
    else:
        weights = weights + np.abs(np.minimum(np.min(weights), 0))
    weights = np.array(weights) / np.sum(weights)
    idxs = np.random.choice(list(range(len(hospitals))), N, p=weights)
    wh = [(weights[idx], hospitals[idx]) for idx in idxs]
    return [h for w,h in sorted(wh, key=lambda x: x[0])]

