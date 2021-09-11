#
def stageFMRCFiles(this):
    from datetime import datetime,timedelta
    """Stage subset and download options for a downloading current  FMRC data
    """
    # Generate times based on timeStride
    def gentimes():
        t = this.subsetOptions.timeRange.start
        while t <= this.subsetOptions.timeRange.end:
            yield t
            t += timedelta(hours=this.subsetOptions.timeStride)
    
    times = list(gentimes())

    # Generate batches of timestamps to include in each file
    max_batch = len(times)
    if ( this.downloadOptions.maxTimesPerFile < 0 or
        this.downloadOptions.maxTimesPerFile > max_batch):
        batch_size = max_batch
    else:
        batch_size = this.downloadOptions.maxTimesPerFile
    
    def genbatches(l,n):
        for i in range(0, len(l), n): 
            yield l[i:i + n]

    batches = list(genbatches(times, batch_size))

    # Stage download records for each file
    # Create a FMRCFile spec for each batch
    
    file_ext = '.nc'  # hardcoded netcdf extension
    # make sure we have the geospatialCoverage
    gsc = c3.FMRCDataArchive(id=this.id).get(include="fmrc.geospatialCoverage").fmrc.geospatialCoverage

    files = [
        c3.FMRCFile(
        **{
            'dataArchive': this,
            'id': (
                this.fmrc.run + '-' + batches[i][0].strftime("%Y-%m-%dT%H:%M:%SZ") + file_ext 
                if this.downloadOptions.maxTimesPerFile == 1 else
                this.fmrc.run + '-' + batches[i][0].strftime("%Y-%m-%dT%H:%M:%SZ") + '-' + batches[i][-1].strftime("%Y-%m-%dT%H:%M:%SZ") + file_ext
            ),
            'timeCoverage': {
                'start': batches[i][0],
                'end': batches[i][-1]
            },
            'timeStride': this.subsetOptions.timeStride,
            'geospatialCoverage': gsc,
            'vars': this.subsetOptions.vars,
            'fileType': this.subsetOptions.accept,
            'status': 'not_downloaded'
        }
        ) for i in range(len(batches))
    ]

    c3.FMRCFile.upsertBatch(objs=files)

    return files
    
