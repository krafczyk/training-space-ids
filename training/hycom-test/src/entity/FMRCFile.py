"""Python Methods for the FMRCFile Type
"""
from urllib.parse import urlencode,urljoin

def download(this, extDir):
    """Download this particular FMRCFile from the Thredds server
    """
    # Get the URL for the thredds server
    url = c3.HycomUtil.createThreddsUrl(this.dataArchive.fmrc.urlPath)

    # Create a fresh instance to avoid version errors or other bs
    updated = c3.FMRCFile(**{'id':this.id})
    updated.status = 'downloading'
    updated.merge()

    try:
        extPath = c3.HycomUtil.downloadToExternal(url, this.id, extDir)
        updated.status='downloaded'
        meta_file = c3.File(**{'url': extPath}).readMetadata()
        updated.file = c3.File(
            **{
                'url': extPath,
                'contentLength': meta_file.contentLength,
                'contentLocation': meta_file.contentLocation,
                'eTag': meta_file.eTag,
                'contentMD5': meta_file.contentMD5,
                'contentType': meta_file.contentType,
                'hasMetadata': True
                }
            )
        updated.merge()
    except Exception as e:
        updated.status = 'error'
        updated.merge()
        raise e
    return updated.file
