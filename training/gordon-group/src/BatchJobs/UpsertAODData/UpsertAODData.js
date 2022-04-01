/**
 * UpsertAODData.js
 * Implementation of UpsertAODData.c3typ
 * @param {UpsertAODData} job
 * @param {UpsertAODDataOptions} options
 */
 function doStart(job, options) {
    var batch = [];

    var dataset = SimulationOutputFile.fetchObjStream({
        filter: "container == 'monthly-mean'",
        limit: -1
    });

    while(dataset.hasNext()) {
        batch.push(dataset.next());

        if (batch.length >= options.batchSize || !dataset.hasNext()) {
            var batchSpec = UpsertDataBatch.make({values: batch});
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
    batch.values.forEach(function(file) {
        file.upsert3HourlyAODAllRefData();
    });
}