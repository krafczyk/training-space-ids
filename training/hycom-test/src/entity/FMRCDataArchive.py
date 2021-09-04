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
    file_ext = '.nc'
    files = [
        c3.FMRCFile(
        **{
            'dataArchive': this,
            'name': (
                this.run + '-' + batches[i][0] + file_ext 
                if this.downloadOptions.maxTimesPerFile == 1 else
                this.run + '-' + batches[i][0] + '-' + batches[i][-1] + file_ext
            ),
            'timeCoverage': {
                'start': batches[i][0],
                'end': batches[i][-1]
            },
            'timeStride': this.subsetOptions.timeStride,
            'geospatialCoverage': this.dataset.geospatialCoverage,
            'vars': this.subsetOptions.vars,
            'fileType': this.subsetOptions.fileType,
            'status': 'not_downloaded'
        }
        ).upsert() for i in range(len(batches))
    ]

    return files
    
