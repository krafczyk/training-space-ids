    """Methods  for Hycom FMRC type"""

def downloadToExternal(srcUrl, fileName, s3_folder):
    import requests
    tmp_path = "/tmp/" + fileName
    with requests.get(srcUrl, stream=True) as r:
        r.raise_for_status()
        with open(tmp_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    c3.Client.uploadLocalClientFiles(tmp_path, s3_folder, {"peekForMetadata": True})
    #c3.Logger.info("file {} downloaded to {}".format(fileName, s3_folder + fileName))
    os.remove(tmp_path)
    return s3_folder + '/' + fileName

####################

def downloadToExternal(srcUrl, fileName, s3_folder):
    import requests
    tmp_path = "/tmp/" + fileName
    with requests.get(srcUrl, stream=True) as r:
        r.raise_for_status()
        with open(tmp_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    c3.Client.uploadLocalClientFiles(tmp_path, s3_folder, {"peekForMetadata": True})
    #c3.Logger.info("file {} downloaded to {}".format(fileName, s3_folder + fileName))
    os.remove(tmp_path)
    return s3_folder + '/' + fileName

def downloadFMRCRunData(this,time_start,time_end,
                      path=None,
                      vars=['surf_el','salinity','water_temp','water_u','water_v'],
                      disableLLSubset='on',
                      disableProjSubset='on',
                      horizStride=1,
                      timeStride=1,
                      vertStride=1,
                      addLatLon='true',
                      accept='netcdf4'
                     ):
    """Download FMRC file and create a HycomFMRCFile instance
    """
    filetypes = ['netcdf','netcdf4']
    if accept not in filetypes:
        raise ValueError(f"Unsupported filetype: {accept} specifed in accept parameter")
    
    file_ext = '.nc'
    
    from urllib.parse import urlencode,urljoin
    
    if path is None:
        path = 'hycom-data'
    
    base_url=f"https://ncss.hycom.org/thredds/ncss/{this.urlPath}"
    #print(base_url)
    varst = [('var',v) for v in vars]
    url1 = urlencode(varst,{'d':2})
    url3 = urlencode({'disableLLSubset':disableLLSubset,
                      'disableProjSubset':disableProjSubset,
                      'horizStride':horizStride,
                      'timeStride':timeStride,
                      'vertStride':vertStride,
                      'addLatLon':addLatLon,
                      'accept':accept
                     })
    
    if (time_start == time_end):
        url2 = urlencode({'time':time_start})
        filename = this.run + '-' + time_start + file_ext
    else:
        url2 = urlencode({'time_start':time_start,'time_end':time_end})
        filename = this.run + '-' + time_start + '-' + time_end + file_ext
        

    query = url1 + '&' + url2 + '&' + url3
    url = base_url+'?'+query
    
    # download file
    file = downloadToExternal(
       srcUrl = url,
       fileName = filename,
       s3_folder = path
    )
    
    # Upsert HycomFMRCFile instance
    
    spec = {
        'hycomFMRC': this,
        'name': filename,
        'timeCoverage': {
            'start': time_start,
            'end': time_end
        },
        'fileType': accept,
        'url': file
    }
    
    fmrc_file = c3.HycomFMRCFile(**spec).upsert()
    
    return fmrc_file
    
