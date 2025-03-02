// FMRCDownloadJob.js

/**
 * 
 * @param {FMRCDownloadJob} job 
 * @param {FMRCDownloadJobOptions} options 
 */
 function doStart(job, options) {
    var batch = []

    var dataset = FMRCFile.fetchObjStream({
        include: '[this, fmrc.expired,fmrc.urlPath]',
        filter: "status != 'downloaded' && fmrc.expired=='false'",
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
/**
 * 
 * @param {FMRCDownloadJobBatch} batch 
 * @param {FMRCDownloadJob} job 
 * @param {FMRCDownloadJobOptions} options 
 */
function processBatch(batch, job, options){

    batch.values.forEach(function(file) {
        file.download()
    });

}
