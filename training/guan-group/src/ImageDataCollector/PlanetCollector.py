## funcions ##

def stage_planet_raw(this):

    import os, requests, json, uuid
    from requests.auth import HTTPBasicAuth
    import urllib.request
    from tqdm import tqdm

    ## batches = c3.PlanetRawFile
    ## use batches to upsert the file using "mergeBatch"
    ## look at "HindcastArchive.py"

    ## checking the condition if no mosaic_id or api_key ##
    if(this.mosaic_id):
        raise ValueError('no mosaic id')
    elif(this.api_key):
        raise ValueError('no api key')

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

    ## insert new PlanetFile ##
    all_files = []
    for i in tqdm(out['items']):
        PRF = c3.PlanetFile(
            **{
                "id": this.id + '_' + i['id'],
                "planet_collector": this.id,
                "name": i['id'],
                "query_url": i['_links']['download']
            }
        )
        all_files.append(PRF)

    return c3.PlanetFile.mergeBatch(objs=all_files)
    

def stage_blob_image(this):

    ##folder_path = c3.FileSystem.inst().urlFromMountAndRelativeEncodedPath(this.base_url)

    '''
    ## modify this image path dictionary ##
    fps = c3.FileSystem.inst().listFiles(folder_path)
    images_path = [] # in theory it will be id and file_path
    for fp in fps.files:
        if(".tif" in fp.contentLocation):
            fp_id = fp.contentLocation.split("/")[-1].split(".tif")[0]
            fp_location = fp.url
            images_path.append({'id': fp_id, 'location': fp_location})

    ## modification for num_images parameters
    images_path = images_path[0:this.num_images]

    ## creating new PlanetFiles ##
    all_files = []
    for i in images_path:
        PRF = c3.PlanetFile(
            **{
                "id": this.id + '_' + i['id'],
                "planet_collector": this.id,
                "name": i['id'],
                "query_url": i['location'],
                "status": "preprocessed",                                       ## this happening because this new dataset is preprocessed already ##
                "processed_image_file": c3.File(**{'url': i['location']}),      ## this happening because this new dataset is preprocessed already ##
                "external_processed_path": i['location']                        ## this happening because this new dataset is preprocessed already ##
            }
        )
        all_files.append(PRF)

    c3.PlanetFile.mergeBatch(objs=all_files)
    '''
    
    
    return this.base_url, this.num_images)