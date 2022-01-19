

def download_raw_image(this):

    import os, requests, json, uuid
    from requests.auth import HTTPBasicAuth
    import urllib.request
    from tqdm import tqdm

    # if the file is already downloaded #
    if(this.status != 'created'):
        raise RuntimeError('The file is already downloaded the raw file')

    def downloadToExternal(srcUrl, fileName, extDir):
        tmp_path = "/tmp/" + fileName
        with requests.get(srcUrl, stream=True) as r:
            r.raise_for_status()
            with open(tmp_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        c3.Client.uploadLocalClientFiles(localPath=tmp_path, dstUrlOrEncodedPath=extDir, spec={"peekForMetadata": True})
        #c3.Logger.info("file {} downloaded to {}".format(fileName, extDir + fileName))
        os.remove(tmp_path)
        return extDir + '/' + fileName

    # create the url for the original source from #
    url = this.query_url

    # create a fresh instance to avoid weird errors #
    updated = c3.PlanetFile(**{'id':this.id})
    updated.status = 'downloading'

    # get the download path #
    download_path = 'yifang_guan/planet_collection/raw/' + this.planet_collector.id + ''

    # create the download #
    try:
        extPath = downloadToExternal(url, this.name + '.tif', download_path)
        updated.status = 'raw'
        updated.raw_image_file = c3.File(**{'url': extPath}).readMetadata()
        updated.external_raw_path = extPath
        updated.merge()
    except Exception as e:
        updated.status = 'error'
        updated.merge()
        raise e

    return updated.external_raw_path


def preprocess_raw_image(this):

    # import gdal and couple other libraries #
    import os
    import gdal

    ## a series checking for this C3 Class and see if it is ready for preprocessing #
    
    # test 1: status check #
    if(this.status != 'raw'):
        raise RuntimeError('The file is not ready to preprocess')
    
    # test 2: raw image file path check #
    updated = c3.PlanetFile(**{'id':this.id})
    if(this.external_raw_path != None):
        try:
            updated.status = 'preprocessing'
            updated.external_processed_path = this.external_raw_path.replace('.tif', '-warp.tif')
            gdal.Warp(updated.external_raw_path.replace, updated.external_processed_path, dstSRS='EPSG:32616', xRes=3, yRes=3)
            updated.merge()
        except Exception as e:
            updated.status = 'error'
            updated.merge()
            raise e

    return updated.external_processed_path
    