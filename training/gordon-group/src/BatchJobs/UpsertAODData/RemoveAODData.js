/**
 * RemoveAODData.js
 * Implementation of RemoveAODData.c3typ
 * @param {RemoveAODData} job
 * @param {UpsertAODDataOptions} options
 */
 function doStart(job, options) {
    var batch = [];

    var dataset = Simulation3HourlyAODOutputAllRef.fetchObjStream({
        limit: options.limit
    });

    while(dataset.hasNext()) {
        batch.push(dataset.next());

        if (batch.length >= options.batchSize || !dataset.hasNext()) {
            var batchSpec = RemoveAODDataBatch.make({values: batch});
            job.scheduleBatch(batchSpec);
            
            batch = [];
        }
    }
}



/**
 * @param {UpsertAODDataBatch} batch
 * @param {UpsertAODData} job
 * @param {UpsertAODDataOptions} options
 */
function processBatch(batch, job, options) {
    Simulation3HourlyAODOutputAllRef.removeBatch(objs=batch)
}