/**
 * RemoveAODData.js
 * Implementation of RemoveAODData.c3typ
 * @param {RemoveAODData} job
 * @param {UpsertAODDataOptions} options
 */
 function doStart(job, options) {
    var batches = [];
    var offset = 0;
    var total = Simulation3HourlyAODOutputAllRef.fetchCount();

    while ((offset + options.batchSize) < total) {
        var fetch_batch = Simulation3HourlyAODOutputAllRef.fetch({
            limit: options.batchSize,
            offset: offset
        }).objs;
        var batchSpec = RemoveAODDataBatch.make({values: fetch_batch});
        batches.push(batchSpec);
        offset += options.batchSize;
    };

    for (var i = 0; i < batches.length; i++) {
        job.scheduleBatch(batches[i]);
    };

}



/**
 * @param {UpsertAODDataBatch} batch
 * @param {UpsertAODData} job
 * @param {UpsertAODDataOptions} options
 */
function processBatch(batch, job, options) {
    Simulation3HourlyAODOutputAllRef.removeBatch(batch.values)
}