from datetime import timedelta
def stageFiles(this):
    # Use downloadOptions to create a modified subsetOptions object
    # Generate a list of all possible times based on timeStride
    batches = c3.HycomUtil.getFileBatches(
        this.subsetOptions.timeRange.start,
        this.subsetOptions.timeRange.end,
        this.subsetOptions.timeStride,
        this.downloadOptions.maxTimesPerFile
    )
    
    file_ext = '.nc'  # hardcoded netcdf extension
    
    files = []
    for i in range(len(batches)):
        # Make a copy of the SubsetOptions for the Archive then adjust
        # the timeRange for this file
        so = c3.HycomSubsetOptions(**this.subsetOptions.toJson())
        so.timeRange = c3.TimeRange( 
            **{
                "start": batches[i][0],
                "end": batches[i][-1]
            }
        )
        name = (
                    this.hindcast.name + '-' + batches[i][0].strftime("%Y-%m-%dT%H:%M:%SZ") + file_ext 
                    if this.downloadOptions.maxTimesPerFile == 1 else
                    this.hindcast.name + '-' + batches[i][0].strftime("%Y-%m-%dT%H:%M:%SZ") + '-' + batches[i][-1].strftime("%Y-%m-%dT%H:%M:%SZ") + file_ext
                )
        file = c3.HindcastFile(
            **{
                "id": this.id + '/' + name,
                "hindcastArchive": this,
                "name": name,
                "start": batches[i][0],
                "end": batches[i][-1],
                "subsetOptions" : so
            }
        )

        files.append(file)
    return c3.HindcastFile.mergeBatch(files)