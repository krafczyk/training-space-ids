"""Methods  for Hycom FMRC type"""

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

def buildThreddsURL(baseurl, vars, options):
    """Builds a Thredds URL for a set of variables and options
    
    Args:
        baseurl (str): base url for the Thredds server + URL path for a run
        vars (list): list of variable names to include in data files
        options (dict): dictionary of options to include in the URL query

    Returns:
        str: Thredds URL
    """
    from urllib.parse import urlencode,urljoin
    varst = [('var',v) for v in vars]
    url1 = urlencode(varst,{'d':2})
    url2 = urlencode(options)
    url = urljoin(baseurl,url1+'&'+url2)
    return url

def stageFMRCFiles(this,archive)):
    from datetime import datetime,timedelta
    """Stage subset and download options for a downloading current  FMRC data
    """

    #if archive_spec is None:
        # Default Data Archive spec
        # archive_spec = {
        #     'fmrc': this,
        #     'subsetOptions': {
        #         'timeRange': {
        #             'start': this.timeCoverage.start,
        #             'end': this.timeCoverage.end
        #         },
        #         'timeStride': 1,
        #         'horizStride': 1,
        #         'vertStride': 1,
        #         'disableLLSubset': 'on',
        #         'disableProjSubset': 'on',
        #         'addLatLon': 'false',
        #         'accept': 'netcdf4',
        #         'vars': ['surf_el','salinity','water_temp','water_u','water_v']
        #     },
        #     'downloadOptions': {
        #         'maxTimesPerFile': 1,
        #     }
        # }

    #archive = c3.FMRCSubsetOptions(**archive_spec).upsert()

    # Now stage download records for each file
    # Genrnate time batches to include in each file
    def gentimes():
        t = archive.subsetOptions.timeRange.start
        while t <= archive.subsetOptions.timeRange.end:
            yield t
            t += timedelta(hours=archive.subsetOptions.timeStride)
    
    times = list(gentimes())
    max_batch = len(times)
    if ( archive.downloadOptions.maxTimesPerFile < 0 or
        archive.downloadOptions.maxTimesPerFile > max_batch):
        batch_size = max_batch
    else:
        batch_size = archive.downloadOptions.maxTimesPerFile
    
    def genbatches(l,n):
        for i in range(0, len(l), n): 
            yield l[i:i + n]

    batches = list(genbatches(times, batch_size))

    # upsert Data archive Record
    archive.upsert()
    # Create a FMRCFile spec for each batch
    #
    file_ext = '.nc'
    files = [
        c3.FMRCFile(
        **{
            'dataArchive': archive,
            'name': (
                this.run + '-' + batches[i][0] + file_ext 
                if archive.downloadOptions.maxTimesPerFile == 1 else
                this.run + '-' + batches[i][0] + '-' + batches[i][-1] + file_ext
            ),
            'timeCoverage': {
                'start': batches[i][0],
                'end': batches[i][-1]
            },
            'timeStride': archive.subsetOptions.timeStride,
            'geospatialCoverage': this.geospatialCoverage,
            'vars': archive.subsetOptions.vars,
            'fileType': archive.subsetOptions.fileType,
            'status': 'not_downloaded'
        }
        ).upsert() for i in range(len(batches))
    ]

    return files
    

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
    
    if time_start == time_end:
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
    
