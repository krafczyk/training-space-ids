import requests
import xmltodict
from datetime import timedelta

#def afterCreate(objs):
#    pass


def upsertFMRCs(this):
    url = this.fmrcCatalogUrl
    with requests.get(url) as r:
        doc = xmltodict.parse(r.text)
    
    frmcs = [ 
        c3.HycomFMRC(
        **{
            'id': d['@ID'],
            'dataset': this,
            'run': d['@name'],
            'urlPath': d['@urlPath'],
            'runDate': d['timeCoverage']['start'],
#            'geospatialCoverage': this.geospatialCoverage,
            'timeCoverage': {
                'start':d['timeCoverage']['start'],
                'end':d['timeCoverage']['end'],
            },
        }
    ).upsert() for d in doc['catalog']['dataset']['dataset']
            ]

    # mark existing FMRCs that are no longer in the catalog as expired
    updates = []
    valid_fmrcs = c3.HycomFMRC.fetch(spec={'filter':"expired==false"}).objs
    if valid_fmrcs:
        for fmrc in valid_fmrcs:
            updated = c3.HycomFMRC(**{'id': fmrc.id,'expired':True})
            for cat in doc['catalog']['dataset']['dataset']:
                if cat['@name'] == fmrc.run:
                    updated.expired = False
                    break
            print (f"{fmrc.run}: {updated.expired}")
            updates.append(updated)
        c3.HycomFMRC.mergeBatch(updates)
    return frmcs

def updateFMRCData(hycomDatasetId, hycomSubsetOptions, hycomDownloadOptions, fmrcDownloadJobOptions):
    """Update FMRC data
        - update FMRCs from Catalog
        For each FMRC:
          - Stage FMRCFiles

        - download each FMRCFile as a batch job

        [Args]
        fmrcSubsetOptions: FMRCSubsetOptions
        fmrcDownloadOptions: FMRCDownloadOptions
        fmrcDownloadJobOptions: FMRCDownloadJobOptions

        [Returns]
        c3.BatchJob
    """
    # Made a static function to pass id in so it will work better as a CronJob
    this = c3.HycomDataset.get(hycomDatasetId)
    
    # Update FMRCs from catalog
    this.upsertFMRCs()
    
    # Loop on unexpired FMRCs and create data archive entries
    valid_fmrcs = c3.HycomFMRC.fetch(spec={'filter':"expired==false"}).objs

    def gentimes(start,end,stride):
        t = start
        while t <= end:
            yield t
            t += timedelta(hours=stride)

    for fmrc in valid_fmrcs:
        so = c3.HycomSubsetOptions(**hycomSubsetOptions.toJson())
        do = c3.HycomDownloadOptions(**hycomDownloadOptions.toJson())
        so.timeRange = c3.TimeRange(
            **{
                'start': fmrc.timeCoverage.start,
                'end': fmrc.timeCoverage.end
            }
        )
        # Bundle all times for the entire FMRC in to 1 file:
        if hycomDownloadOptions.maxTimesPerFile == -1:
            do.maxTimesPerFile = len(list(gentimes(fmrc.timeCoverage.start,fmrc.timeCoverage.end,1)))
        fmrc.stageFMRCFiles(so, do)

    # Submit Batch Job to Download all files
    job = c3.FMRCDownloadJob(**{'options': fmrcDownloadJobOptions.toJson()}).upsert()
    job.start()
        
    return job