## funcions ##

def stage_planet_raw(this):

    import os, requests, json, uuid
    from requests.auth import HTTPBasicAuth
    import urllib.request
    from tqdm import tqdm

    ## batches = c3.PlanetRawFile
    ## use batches to upsert the file using "mergeBatch"
    ## look at "HindcastArchive.py"

    ## create the auth ##
    auth = HTTPBasicAuth(this.api_key, '')
    ## create the full path of the url ##
    url = f'{this.base_url}{this.mosaic_id}/quads'
    ## create bbox: pattern lon, lat, lon, lat ##
    bbox = str(this.start_lon) + ", " + str(this.start_lat) + ", " + str(this.end_lon) + ", " + str(this.end_lat)
    
    ## start the request ##
    res = requests.get(url=url, auth=auth, params={'bbox': bbox, '_page_size': 99999})
    ## json the result ##
    out = json.loads(res.text)

    ## insert new PlanetRawFile ##
    all_files = []
    for i in tqdm(out['items']):
        PRF = c3.PlanetRawFile(
            **{
                "id": this.id + '_' + i['id'],
                "planet_collector": this,
                "name": i['id'],
                "query_url": i['_links']['download']
            }
        )
        all_files.append(PRF)

    return c3.PlanetRawFile.mergeBatch(all_files)
    
