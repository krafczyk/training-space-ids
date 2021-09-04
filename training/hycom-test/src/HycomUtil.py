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

def buildThreddsUrl(baseurl, vars, options):
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