"""Python Methods for the FMRCFile Type
"""
def download(this):
    """Download this particular FMRCFile from the Thredds server
    """
    from urllib.parse import urlencode,urljoin

    if this.dataArchive.subsetOptions is None or this.dataArchive.fmrc is None:
        dataArchive = c3.FMRCDataArchive.get(this.dataArchive.id)
    else:
        dataArchive = this.dataArchive
    fmrc = dataArchive.fmrc

    if fmrc.urlPath is None:
        fmrc = c3.HycomFMRC.get(this.dataArchive.fmrc.id)

    url_path = fmrc.urlPath
    
    baseurl = urljoin('https://ncss.hycom.org/thredds/ncss/grid',url_path)

    # Convert FMRCSubsetOptions object to a dictionary
    options = {
        'disableLLSubset': dataArchive.subsetOptions.disableLLSubset,
        'disableProjSubset': dataArchive.subsetOptions.disableProjSubset,
        'horizStride': dataArchive.subsetOptions.horizStride,
        'timeStride': dataArchive.subsetOptions.timeStride,
        'vertStride': dataArchive.subsetOptions.vertStride,
        'addLatLon': dataArchive.subsetOptions.addLatLon,
        'accept': dataArchive.subsetOptions.accept
        }

    time_start = this.timeCoverage.start
    time_end = this.timeCoverage.end

    if time_start == time_end:
        options ['time'] = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        options['time_start'] = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
        options['time_end'] = time_end.strftime("%Y-%m-%dT%H:%M:%SZ")

    vars_list = this.vars.split(',')
    vars = [('var',v) for v in vars_list]
    url1 = urlencode(vars,{'d':2})
    url2 = urlencode(options)
    url = baseurl + '?' + url1 + '&' + url2

    this.status = 'downloading'
    this.upsert()

    try:
        extPath = c3.HycomUtil.downloadToExternal(url, this.fileName, 'hycom-data')
        this.status='downloaded'
        this.file = c3.File(**{'url': extPath})
        this.upsert()
    except Exception as e:
        this.status = 'error'
        this.upsert()
        raise e
    return url
