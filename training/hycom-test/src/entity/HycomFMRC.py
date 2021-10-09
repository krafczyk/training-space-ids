"""Python Methods  for HycomFMRC type"""

def stageFMRCFiles(this):
    from datetime import datetime,timedelta
    """Stage subset and download options for a downloading current  FMRC data
    """
    # Generate a list of all possible times based on timeStride
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
    #gsc = c3.FMRCDataArchive(id=this.id).get(include="fmrc.geospatialCoverage").fmrc.geospatialCoverage
    #if gsc is None:
    #    raise Exception("Missing geospatialCoverage")

    # Note, the status is explicitly not merged here so that the post default will kick in if needed
    # and already "downloaded" files don't get re-downloaded
    files = [
        c3.FMRCFile(
        **{
            'fmrc': this,
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
            #'geospatialCoverage': ,
            'vars': this.subsetOptions.vars,
            'fileType': this.subsetOptions.accept
        }
        ) for i in range(len(batches))
    ]

    c3.FMRCFile.mergeBatch(objs=files)

    # Update staged field
    #this.staged = True
    #this.merge()

    return files
# def updateFMRCData(fmrcSubsetOptions, fmrcDownloadOptions, fmrcDownloadJobOptions):
#     """Update FMRC data
#         - update FMRCs from Catalog
#         For each FMRC:
#           - Create FMRCDataArchive entries
#           - Stage FMRCFiles

#         - download each FMRCFile as a batch job

#         [Args]
#         fmrcSubsetOptions: FMRCSubsetOptions
#         fmrcDownloadOptions: FMRCDownloadOptions
#         fmrcDownloadJobOptions: FMRCDownloadJobOptions

#         [Returns]
#         c3.BatchJob
#     """
#     def make_data_archive(fmrc):
#         #print(fmrc)
#         fmrcSubsetOptions.timeRange = c3.TimeRange(
#             **{
#                 'start': fmrc.timeCoverage.start,
#                 'end': fmrc.timeCoverage.end
#             }
#         )
#         return c3.FMRCDataArchive(
#             **{
#                 'id': fmrc.id,
#                 'fmrc': fmrc,
#                 'subsetOptions': fmrcSubsetOptions.toJson(),
#                 'downloadOptions': fmrcDownloadOptions.toJson()
#             }
#         )
    
#     # Update FMRCs from catalog
#     gom_dataset=c3.HycomDataset.get('GOMu0.04_901m000_FMRC_1.0.1')
#     gom_dataset.upsertFMRCs()
    
#     # Loop on unexpired FMRCs and create data archive entries
#     valid_fmrcs = c3.HycomFMRC.fetch(spec={'filter':"expired==false"}).objs
#     for fmrc in valid_fmrcs:
#         da = make_data_archive(fmrc)
#         da.upsert()
#         #print(da)
#         da.stageFMRCFiles()
        
#     # Submit Batch Job to Download all files
#     job = c3.FMRCDownloadJob(**{'options': fmrcDownloadJobOptions.toJson()}).upsert()
#     job.start()
        
#     return job