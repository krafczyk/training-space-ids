def download(this):
    url = c3.HycomUtil.createThreddsUrl(this.hindcastArchive.hindcast.urlPath, this.subsetOptions)
    #print(url)
    # Create a fresh instance to avoid version errors or other bs
    updated = c3.HindcastFile(**{'id':this.id})
    updated.status = 'downloading'
    updated.merge()
    
    download_path = this.hindcastArchive.downloadOptions.externalDir + '/hindcast/' + this.hindcastArchive.id
    
    try:
        extPath = c3.HycomUtil.downloadToExternal(url, this.name, download_path)
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