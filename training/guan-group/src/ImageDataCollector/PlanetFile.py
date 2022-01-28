

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
    defined_download_path = 'yifang_guan/planet_collection/raw/' + this.planet_collector.id + ''

    # create the download #
    try:
        extPath = downloadToExternal(url, this.name + '.tif', defined_download_path)
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

    ## changing the GDAL env path to find proj package ##
    os.environ['PROJ_LIB'] = '/home/c3/.conda/envs/py-image/share/proj'
    os.environ['GDAL_DATA'] = '/home/c3/.conda/envs/py-image/share'

    ## a series checking for this C3 Class and see if it is ready for preprocessing #
    
    # test 1: status check #
    if(this.status != 'raw'):
        raise RuntimeError('The file is not ready to preprocess')

    def get_encoded_path(path):
        """
        Trim local fs url to absolute path
        e.g. from "file:///tmp/d.txt" to "/tmp/d.txt"
        """
        if path.startswith("file://"):
            return path[7:]
        return path

    def local_file(base_path):
        """
        Downloads file locally
        :param base_path: string to remote file system url
        :return: temp_path: string to local file system path
        """
        file = c3.LocalFileSystem.makeTmpFile().url
        c3.Client.copyFilesToLocalClient(srcUrlOrEncodedPath=base_path, localPath=file)
        temp_path = os.path.join(get_encoded_path(file), os.path.basename(base_path))
        return temp_path

    ## creating the tmp file in the space
    tmp_url = this.raw_image_file.url
    tmp_local = local_file(tmp_url)

    # test 2: raw image file path check #
    updated = c3.PlanetFile(**{'id':this.id})
    if(this.external_raw_path != None):
        try:
            ## print(updated.external_processed_path, updated.external_raw_path)
            updated.status = 'preprocessing'
            updated.external_processed_path = this.external_raw_path.replace('.tif', '-warp.tif')
            gdal_raw_fp = this.raw_image_file.contentLocation
            gdal_preprocessed_fp = gdal_raw_fp.replace('.tif', '-warp.tif')
            ## using the full path ##
            ## gdal.Warp(gdal_preprocessed_fp, gdal_raw_fp, dstSRS='EPSG:32616', xRes=3, yRes=3)
            ds = gdal.Open(tmp_local)
            gdal.Warp(srcDSOrSrcDSTab=ds, destNameOrDestDS=updated.external_processed_path, dstSRS='EPSG:32616', xRes=3, yRes=3)
            
            updated.merge()
        except Exception as e:
            updated.status = 'error'
            updated.merge()
            raise e

    return updated.external_processed_path

def predict_image(this):

    

    return None
    