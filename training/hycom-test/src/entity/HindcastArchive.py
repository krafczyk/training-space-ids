def downloadLocal(this, hycomSubsetOptions, localDir):

    url_path = this.urlPath
    
    baseurl = urljoin('https://ncss.hycom.org/thredds/ncss/grid',url_path)

    # Convert FMRCSubsetOptions object to a dictionary
    options = {
        'disableLLSubset': hycomSubsetOptions.disableLLSubset,
        'disableProjSubset': hycomSubsetOptions.disableProjSubset,
        'horizStride': hycomSubsetOptions.horizStride,
        'timeStride': hycomSubsetOptions.timeStride,
        'vertStride': hycomSubsetOptions.vertStride,
        'addLatLon': hycomSubsetOptions.addLatLon,
        'accept': hycomSubsetOptions.accept
        }
    
    # Handle time coverage separately
    time_start = hycomSubsetOptions.timeRange.start
    time_end = hycomSubsetOptions.timeRange.start

    if time_start == time_end:
        options ['time'] = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        options['time_start'] = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
        options['time_end'] = time_end.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Construt query url
    vars_list = hycomSubsetOptions.vars.split(',')
    vvars = [('var',v) for v in vars_list]
    url1 = urlencode(vvars,{'d':2})
    url2 = urlencode(options)
    url = baseurl + '?' + url1 + '&' + url2
    
    print(url)

    localPath = c3.HycomUtil.downloadToLocal(url, this.id + ".nc", localDir)
    
    return localPath