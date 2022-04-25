/**
 * Implementation of CreateSimulationFileTable.c3typ
 * @param {CreateSimulationFileTable} jobtype
 * @param {CreateSimulationFileTableOptions} joboptions
 */
 function doStart(job, options) {
    var batch = [];

    for (var i = 0; i < job.simulationSamples.length; i++) {
        batch.push(job.simulationSamples[i]);

        if (batch.length >= options.batchSize || i == job.simulationSamples.length - 1) {
            var batchSpec = CreateSimulationFileTableBatch.make({values: batch});
            job.scheduleBatch(batchSpec);
            
            batch = [];
        }
    }
}

/**
 * @param {CreateSimulationFileTableBatch} batch
 * @param {CreateSimulationFileTable} job
 * @param {CreateSimulationFileTableOptions} options
 */
 function processBatch(batch, job, options) {
    batch.values.forEach(function(simulationSample) {
        simulationSample.upsertFileTable();
    });
}