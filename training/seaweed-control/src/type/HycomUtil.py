from urllib.parse import urlencode,urljoin
from datetime import timedelta

def downloadToLocal(srcUrl, fileName, localDir="/tmp"):
    """
    """
    import os
    import requests
    tmp_path = localDir + "/" + fileName
    with requests.get(srcUrl, stream=True) as r:
        r.raise_for_status()
        with open(tmp_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return tmp_path

def downloadToExternal(srcUrl, fileName, extDir):
    """
    """
    import os
    import requests
    tmp_path = "/tmp/" + fileName
    with requests.get(srcUrl, stream=True) as r:
        r.raise_for_status()
        with open(tmp_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    c3.Client.uploadLocalClientFiles(tmp_path, extDir, {"peekForMetadata": True})
    #c3.Logger.info("file {} downloaded to {}".format(fileName, extDir + fileName))
    os.remove(tmp_path)
    return extDir + '/' + fileName

def nc_open(url, local_path='/tmp'):
    """Opens a netCDF file from an external storage path
    
    Args:
        url (str): URL to a netCDF file
        local_path (str): Path to the local file
    
    Returns:
        netCDF4.Dataset: A netCDF4 Dataset object
    """
    import netCDF4 as nc
    import os
    filename = os.path.basename(url) 
    tmp_path = local_path + '/' + filename
    c3.Client.copyFilesToLocalClient(url,'/tmp')
    return nc.Dataset(tmp_path)

def nc_close(ds, url, local_path='/tmp'):
    """Closes a netCDF file
    
    Args:
        ds (netCDF4.Dataset): A netCDF4 Dataset object
        url (str): URL to a netCDF file
        local_path (str): Path to the local file
    """
    import os
    ds.close()
    filename = os.path.basename(url) 
    tmp_path = local_path + '/' + filename
    os.remove(tmp_path)
    return 1


# 
def createThreddsUrl(urlPath, subsetOptions):
    
    baseurl = urljoin('https://ncss.hycom.org/thredds/ncss/grid',urlPath)

    # Convert part of subsetOptions object to a dictionary
    options = {
        'disableProjSubset': subsetOptions.disableProjSubset,
        'horizStride': subsetOptions.horizStride,
        'timeStride': subsetOptions.timeStride,
        'addLatLon': subsetOptions.addLatLon,
        'accept': subsetOptions.accept
        }
    if subsetOptions.vertCoord == -1:
        options['vertStride'] = subsetOptions.vertStride
    else:
        options['vertCoord'] = subsetOptions.vertCoord

    # Handle time coverage separately
    time_start = subsetOptions.timeRange.start
    time_end = subsetOptions.timeRange.end

    if time_start == time_end:
        options ['time'] = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        options['time_start'] = time_start.strftime("%Y-%m-%dT%H:%M:%SZ")
        options['time_end'] = time_end.strftime("%Y-%m-%dT%H:%M:%SZ")

    if subsetOptions.disableLLSubset == "on":
        options['disableLLSubset'] = "on"
    else:
        options['north'] = subsetOptions.geospatialCoverage.end.latitude
        options['south'] = subsetOptions.geospatialCoverage.start.latitude
        options['east'] = subsetOptions.geospatialCoverage.end.longitude
        options['west'] = subsetOptions.geospatialCoverage.start.longitude

    # Construct query url
    vars_list = subsetOptions.vars.split(',')
    vvars = [('var',v) for v in vars_list]
    url1 = urlencode(vvars,{'d':2})
    url2 = urlencode(options)
    url = baseurl + '?' + url1 + '&' + url2
    
    return url

def getFileBatches(start, end, stride, timesPerFile):
        def gentimes():
            t = start
            while t <= end:
                yield t
                t += timedelta(hours=stride)

        times = list(gentimes())

        # Generate batches of timestamps to include in each file
        max_batch = len(times)
        if ( timesPerFile < 0 or
            timesPerFile > max_batch):
            batch_size = max_batch
        else:
            batch_size = timesPerFile

        def genbatches(l,n):
            for i in range(0, len(l), n): 
                yield l[i:i + n]

        return list(genbatches(times, batch_size))

def testenv():
    import hj_reachability
    import ocean_simulation_navigator