/**
 * RemoveAODData.js
 * Implementation of RemoveAODData.c3typ
 * @param {RemoveAODData} job
 * @param {UpsertAODDataOptions} options
 */
 function doStart(job, options) {
    var batch = [];

    while(Simulation3HourlyAODOutputAllRef.exists()) {
        var fetch_batch = Simulation3HourlyAODOutputAllRef.fetch({
            limit: options.limit
        })
        batch = fetch_batch.objs;
        var batchSpec = RemoveAODDataBatch.make({values: batch});
        job.scheduleBatch(batchSpec);

        batch = [];
    }

}



/**
 * @param {UpsertAODDataBatch} batch
 * @param {UpsertAODData} job
 * @param {UpsertAODDataOptions} options
 */
function processBatch(batch, job, options) {
    Simulation3HourlyAODOutputAllRef.removeBatch(batch)
}