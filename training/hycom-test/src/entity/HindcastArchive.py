from datetime import datetime, timedelta

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

def updateTimeRange(this,timeRange):
    tr1 = this.subsetOptions.timeRange
    tr2 = timeRange
    # check that requested time intersects with original
    if (
        not (((tr1.start <= tr2.start <= tr1.end) or 
        (tr2.start <= tr1.start <= tr2.end)) and 
        ((tr2.end >= tr1.end) and
        (tr2.start <= tr1.start)))
    ):
        raise ValueError('The requested updated timeRange does not encompass the original.')
    print("good") 
        
    # check that the requested time does not fall out of range for the archive year
    
    # update the subset options
    new_archv = c3.HindcastArchive(**this.toJson())
    new_archv.subsetOptions.timeRange = timeRange
    new_archv.merge(spec={'mergeInclude': 'subsetOptions'})

    new_archv.stageFiles()
    return new_archv