def download(this):
    url = c3.HycomUtil.createThreddsUrl(this.hindcastArchive.hindcast.urlPath, this.subsetOptions)
    #print(url)
    # Create a fresh instance to avoid version errors or other bs
    updated = c3.HindcastFile(**{'id':this.id})
    updated.status = 'downloading'
    updated.threddsUrl = url
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

# Prototype for prosessing hindcast files
from datetime import datetime, timedelta
from itertools import islice

def chunk(gen, k):
    """Chunk a generator into batches of size k 
    """
    while True:
        chunk = [*islice(gen, 0, k)]
        if chunk:
            yield chunk
        else:
            break

def upsertFunc(objs):
    c3.SurfaceHindcastData.upsertBatch(objs)

def process(this,chunkSize=23400,maxConcurrency=8):
    """ Process a single Hindcast NetCDF file into the Hindcast__Data types"""
    # extract surface data for a variable
    hycom_file = c3.HycomUtil.nc_open(this.file.url)
    
    # extract lat-long, or derive this from types
    # Not yet done:determine the offset for each based on the subsetOptions for this file
    # Note: for now it's just an integer list assuming full converage
    xsz = len(hycom_file['lon'])
    ysz = len(hycom_file['lat'])
    latitudes = range(ysz)
    longitudes = range(xsz)
    
    # Generate a list of times that the file contains
    def gentimes(start,end,stride):
        t = start
        while t <= end:
            yield t
            t += timedelta(hours=stride)
    
    times = list(gentimes(this.start,this.end,this.subsetOptions.timeStride))
    #print (f"Processing {len(times)} timeSteps:")
    #t1 = [times[24]]

    # Loop over timesteps
    # Use a generator to instatiate types in batches
    actions = []
    it = 0
    def idx(i,j):
        return ysz*i  + j
    for time in times:
        print(f"Processing for time step: {time}")
        water_u = hycom_file.variables['water_u'][:].data[it,0,:,:]
        water_v = hycom_file.variables['water_v'][:].data[it,0,:,:]
        
        genRecords = (
            c3.SurfaceHindcastData(
                **{
                    'start': time,
                    'parent' : c3.SurfaceHindcastDataSeries(
                        id = 'HNDCST_SRFC_' + str(i) + '-' + str(j)
                    ).toJson(),
                    'name': 'water_u',
                    'water_u': water_u[i,j],
                    'water_v': water_v[i,j]
                }
            )
            for i in latitudes
                for j in longitudes
        )
        
        # ic = 1
        # for objs in chunk(genRecords,chunkSize):
        #     print (f"Submiting Async for chunk: {ic} {chunkSize}")

        #     action = c3.AsyncAction.submit({
        #         'typeName': "SurfaceHindcastData",
        #         'action': 'upsertBatch',
        #         'args': {
        #             'objs': c3.c3Make("[SurfaceHindcastData]",objs)
        #          }
        #     })
        #     actions.append(action)

        #     ic += 1
            
        print(f"Loading {xsz*ysz} records, chunkSize: {chunkSize}, maxConcurrency: {maxConcurrency}")
        _ = c3.Client.executeConcurrently(upsertFunc,[(x,) for x in chunk(genRecords,chunkSize)],maxConcurrency)

        it += 1

        update = c3.HindcastFile(
            **{
                "id": this.id,
                "stepsProcessed": it
            }
        ).merge()

    # close the file
    c3.HycomUtil.nc_close(ds=hycom_file, url=this.file.url)
    
    update = c3.HindcastFile(
        **{
            "id": this.id,
            "processed": True
        }
    ).merge()
    total = len(times)*xsz*ysz

    return total