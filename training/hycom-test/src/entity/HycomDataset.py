import requests
import xmltodict
#from urllib.parse import urlencode,urljoin



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
    
def buildHycomFMRCUrl(urlpath,time_start,time_end,
                      vars=['surl_el','salinity','water_temp','water_u','water_v'],
                      disableLLSubset='on',
                      disableProjSubset='on',
                      horizStride=1,
                      timeStride=1,
                      vertStride=1,
                      addLatLon='true',
                      accept='netcdf4'
                     ):
    base_url=f"https://ncss.hycom.org/thredds/ncss/{urlpath}"
    #print(base_url)
    varst = [('var',v) for v in vars]
    url1 = urlencode(varst,{'d':2})
    url2 = urlencode({'disableLLSubset':disableLLSubset,
                      'disableProjSubset':disableProjSubset,
                      'horizStride':horizStride,
                      'time_start':time_start,
                      'time_end':time_end,
                      'timeStride':timeStride,
                      'vertStride':vertStride,
                      'addLatLon':addLatLon,
                      'accept':accept
                     })
    query = url1+'&'+url2
    url = base_url+'?'+query
    return url  



def upsertFMRCFromDatasetCatalog(this):
    url = this.catalog_url
    with requests.get(url) as r:
        doc = xmltodict.parse(r.text)
    
    frmcs = [ 
        c3.HycomFMRC(
        **{
            'id': d['@ID'],
            'dataset': this,
            'run': d['@name'],
            'timeCoverage': {
                'start':d['timeCoverage']['start'],
                'end':d['timeCoverage']['end'],
            },
            'thredds_url': buildHycomFMRCUrl(
                   urlpath = d['@urlPath'],
                   time_start = d['timeCoverage']['start'],
                   time_end = d['timeCoverage']['end']
                   )
        }
    ).upsert() for d in doc['catalog']['dataset']['dataset']
            ]
    return frmcs