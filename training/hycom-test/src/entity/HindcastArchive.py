from datetime import timedelta
def stageFiles(this):
    # Use downloadOptions to create a modified subsetOptions object
    
    # Make this a util function
    # # Generate a list of all possible times based on timeStride
    # def getFileBatches(start, end, stride, timesPerFile):
    #     def gentimes():
    #         t = start
    #         while t <= end:
    #             yield t
    #             t += timedelta(hours=stride)

    #     times = list(gentimes())

    #     # Generate batches of timestamps to include in each file
    #     max_batch = len(times)
    #     if ( timesPerFile < 0 or
    #         timesPerFile > max_batch):
    #         batch_size = max_batch
    #     else:
    #         batch_size = timesPerFile

    #     def genbatches(l,n):
    #         for i in range(0, len(l), n): 
    #             yield l[i:i + n]

    #     return list(genbatches(times, batch_size))
    
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