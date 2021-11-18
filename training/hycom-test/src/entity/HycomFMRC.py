"""Python Methods  for HycomFMRC type"""

def stageFMRCFiles(this, subsetOptions, downloadOptions):
    from datetime import datetime,timedelta
    """Stage subset and download options for a downloading current  FMRC data
    """
    # # Generate a list of all possible times based on timeStride
    # def gentimes():
    #     t = subsetOptions.timeRange.start
    #     while t <= subsetOptions.timeRange.end:
    #         yield t
    #         t += timedelta(hours=subsetOptions.timeStride)
    
    # times = list(gentimes())

    # # Generate batches of timestamps to include in each file
    # max_batch = len(times)
    # if ( downloadOptions.maxTimesPerFile < 0 or
    #     downloadOptions.maxTimesPerFile > max_batch):
    #     batch_size = max_batch
    # else:
    #     batch_size = downloadOptions.maxTimesPerFile
    
    # def genbatches(l,n):
    #     for i in range(0, len(l), n): 
    #         yield l[i:i + n]

    # batches = list(genbatches(times, batch_size))

    batches = c3.HycomUtil.getFileBatches(
        subsetOptions.timeRange.start,
        subsetOptions.timeRange.end,
        subsetOptions.timeStride,
        downloadOptions.maxTimesPerFile
    )

    # Stage download records for each file
    # Create a FMRCFile spec for each batch
    
    file_ext = '.nc'  # hardcoded netcdf extension

    files = []
    for i in range(len(batches)):
        # Make a copy of the SubsetOptions for the Archive then adjust
        # the timeRange for this file
        so = c3.HycomSubsetOptions(**subsetOptions.toJson())
        so.timeRange = c3.TimeRange( 
            **{
                "start": batches[i][0],
                "end": batches[i][-1]
            }
        )
        name = (
                this.run + '-' + batches[i][0].strftime("%Y-%m-%dT%H:%M:%SZ") + file_ext 
                if downloadOptions.maxTimesPerFile == 1 else
                this.run + '-' + batches[i][0].strftime("%Y-%m-%dT%H:%M:%SZ") + '-' + batches[i][-1].strftime("%Y-%m-%dT%H:%M:%SZ") + file_ext
            )
        file = c3.FMRCFile(
            **{
                'id': name,
                'fmrc': this,
                'name': name,
                'subsetOptions': so,

            }
        )
        files.append(file)

    files_merged = c3.FMRCFile.mergeBatch(files)

    return len(files_merged)

    # # Note, the status is explicitly not merged here so that the post default will kick in if needed
    # # and already "downloaded" files don't get re-downloaded
    # files = [
    #     c3.FMRCFile(
    #     **{
    #         'fmrc': this,
    #         'id': (
    #             this.run + '-' + batches[i][0].strftime("%Y-%m-%dT%H:%M:%SZ") + file_ext 
    #             if downloadOptions.maxTimesPerFile == 1 else
    #             this.run + '-' + batches[i][0].strftime("%Y-%m-%dT%H:%M:%SZ") + '-' + batches[i][-1].strftime("%Y-%m-%dT%H:%M:%SZ") + file_ext
    #         ),
    #         'timeCoverage': {
    #             'start': batches[i][0],
    #             'end': batches[i][-1]
    #         },
    #         'timeStride': subsetOptions.timeStride,
    #         #'geospatialCoverage': ,
    #         'vars': subsetOptions.vars,
    #         'fileType': subsetOptions.accept
    #     }
    #     ) for i in range(len(batches))
    # ]

    # update = c3.HycomFMRC (
    #     **{
    #         'id': this.id,
    #         'subsetOptions': subsetOptions,
    #         'downloadOptions': downloadOptions,
    #     }
    # )
    # update.merge()

    # c3.FMRCFile.mergeBatch(objs=files)

    # # Update staged field
    # #this.staged = True
    # #this.merge()

    # return files