// FMRCDownloadJob.js

/**
 * 
 * @param {FMRCDownloadJob} job 
 * @param {FMRCDownloadJobOptions} options 
 */
 function doStart(job, options) {
    var batch = []

    var dataset = FMRCFile.fetchObjStream({
        include: '[this, dataArchive.fmrc,dataArchive.fmrc.expired,dataArchive.fmrcDownloadOptions]',
        filter: "status != 'downloaded' && dataArchive.fmrc.expired=='false'",
        limit: options.limit,
    });
    while(dataset.hasNext()) {
        batch.push(dataset.next());

        // Break dataset in batches and schedule them for processing
        if(dataset.length >= options.batchSize || !dataset.hasNext()) {
            var batchSpec = FMRCDownloadJobBatch.make({values: batch});
            job.scheduleBatch(batchSpec);

            batch = [];
        }
    }
}