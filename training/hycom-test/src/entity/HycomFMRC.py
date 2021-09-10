"""Python Methods  for HycomFMRC type"""

def updateFMRCData(fmrcSubsetOptions, fmrcDownloadOptions, fmrcDownloadJobOptions):
    """Update FMRC data
        - update FMRCs from Catalog
        For each FMRC:
          - Create FMRCDataArchive entries
          - Stage FMRCFiles

        - download each FMRCFile as a batch job

        [Args]
        fmrcSubsetOptions: FMRCSubsetOptions
        fmrcDownloadOptions: FMRCDownloadOptions
        fmrcDownloadJobOptions: FMRCDownloadJobOptions

        [Returns]
        c3.BatchJob
    """
    def make_data_archive(fmrc):
        #print(fmrc)
        fmrcSubsetOptions.timeRange = c3.TimeRange(
            **{
                'start': fmrc.timeCoverage.start,
                'end': fmrc.timeCoverage.start
            }
        )
        return c3.FMRCDataArchive(
            **{
                'id': fmrc.id,
                'fmrc': fmrc,
                'subsetOptions': fmrcSubsetOptions.toJson(),
                'downloadOptions': fmrcDownloadOptions.toJson()
            }
        )
    
    # Update FMRCs from catalog
    gom_dataset=c3.HycomDataset.get('GOMu0.04_901m000_FMRC_1.0.1')
    gom_dataset.upsertFMRCs()
    
    # Loop on unexpired FMRCs and create data archive entries
    valid_fmrcs = c3.HycomFMRC.fetch(spec={'filter':"expired==false"}).objs
    for fmrc in valid_fmrcs:
        da = make_data_archive(fmrc)
        da.upsert()
        print(da)
        da.stageFMRCFiles()
        
    # Submit Batch Job to Download all files
    job = c3.FMRCDownloadJob(**{'options': fmrcDownloadJobOptions.toJson()}).upsert()
    job.start()
        
    return job