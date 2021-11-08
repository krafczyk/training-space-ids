// HindcastProcessJob.js

/**
 * 
 * @param {HindcastProcessJob} job 
 * @param {HycomProcessJobOptions} options 
 */
 function doStart(job, options) {
    var batch = []

    var dataset = HindcastFile.fetchObjStream({
        include: '[this]',
        filter: "processed == false",
        limit: options.limit
    });
    while(dataset.hasNext()) {
        batch.push(dataset.next());

        // Break dataset in batches and schedule them for processing
        if(dataset.length >= options.batchSize || !dataset.hasNext()) {
            var batchSpec = HindcastProcessJobBatch.make({values: batch});
            job.scheduleBatch(batchSpec);

            batch = [];
        }
    }
}
/**
 * 
 * @param {HindcastProcessJobBatch} batch 
 * @param {HindcastProcessJob} job 
 * @param {HycomProcessJobOptions} options 
 */
function processBatch(batch, job, options){

    batch.values.forEach(function(file) {
        file.process(options.chunkSize, options.maxConcurrency);
    });

}