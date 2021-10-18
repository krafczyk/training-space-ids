// FMRCDownloadJob.js

/**
 * 
 * @param {HindcastDownloadJob} job 
 * @param {HycomDownloadJobOptions} options 
 */
 function doStart(job, options) {
    var batch = []

    var dataset = HindcastFile.fetchObjStream({
        include: '[this]',
        filter: "status != 'downloaded'",
        limit: options.limit,
    });
    while(dataset.hasNext()) {
        batch.push(dataset.next());

        // Break dataset in batches and schedule them for processing
        if(dataset.length >= options.batchSize || !dataset.hasNext()) {
            var batchSpec = HindcastDownloadJobBatch.make({values: batch});
            job.scheduleBatch(batchSpec);

            batch = [];
        }
    }
}
/**
 * 
 * @param {HindcastDownloadJobBatch} batch 
 * @param {HindcastDownloadJob} job 
 * @param {HycomDownloadJobOptions} options 
 */
function processBatch(batch, job, options){

    batch.values.forEach(function(file) {
        file.download();
    });

}
