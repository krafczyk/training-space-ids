import requests
import xmltodict


def upsertHycomDatasetFromCatalog(url=None):
    """
    Query Hycom catalog and create HycomDataset object.
    should add try/except for bad request
    """
    with requests.get(url) as r:
        doc = xmltodict.parse(r.text)

    name = doc['catalog']['@name']
    version = doc['catalog']['@version']
    id = name.rpartition('/')[2]+'_'+version
    lat_start = float(doc['catalog']['dataset']['metadata']['geospatialCoverage']['northsouth']['start'])
    lat_size = float(doc['catalog']['dataset']['metadata']['geospatialCoverage']['northsouth']['size'])
    lon_start = float(doc['catalog']['dataset']['metadata']['geospatialCoverage']['eastwest']['start'])
    lon_size = float(doc['catalog']['dataset']['metadata']['geospatialCoverage']['eastwest']['size'])
    
    dataset_spec = {
        'id': id,
        'name': id,
        'description': name,
        'hycom_version': version,
        'geospatialCoverage': {
            'start': {
                'latitude': lat_start,
                'longitude': lon_start
            },
            'end': {
                'latitude': lat_start + lat_size,
                'longitude': lon_start + lon_size
            }
        },
        'catalog_url': url
        
    }
    dataset = c3.HycomDataset(**dataset_spec)
    dataset.upsert()
    #print(dataset_spec)
    return dataset
    


def upsertFMRCs(this):
    url = this.catalog_url
    with requests.get(url) as r:
        doc = xmltodict.parse(r.text)
    
    frmcs = [ 
        c3.HycomFMRC(
        **{
            'id': d['@ID'],
            'dataset': this,
            'run': d['@name'],
            'urlPath': d['@urlPath'],
            'geospatialCoverage': this.geospatialCoverage,
            'timeCoverage': {
                'start':d['timeCoverage']['start'],
                'end':d['timeCoverage']['end'],
            },
        }
    ).upsert() for d in doc['catalog']['dataset']['dataset']
            ]

    # mark existing FMRCs that are no longer in the catalog as expired
    updates = []
    valid_fmrcs = c3.HycomFMRC.fetch(spec={'filter':"expired==false"}).objs
    if valid_fmrcs:
        for fmrc in valid_fmrcs:
            updated = c3.HycomFMRC(**{'id': fmrc.id,'expired':True})
            for cat in doc['catalog']['dataset']['dataset']:
                if cat['@name'] == fmrc.run:
                    updated.expired = False
                    break
            print (f"{fmrc.run}: {updated.expired}")
            updates.append(updated)
        c3.HycomFMRC.mergeBatch(updates)
    return frmcs