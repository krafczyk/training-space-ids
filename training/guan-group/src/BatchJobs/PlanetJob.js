

/**
 * 
 */
 function doStart(job, options) {
    var batch = []

    var dataset = PlanetFile.fetchObjStream({
        include: '[this]',
        filter: options.filter,
        limit: options.limit
    });
    while(dataset.hasNext()) {
        batch.push(dataset.next());

        // Break dataset in batches and schedule them for processing
        if(batch.length >= options.batchSize || !dataset.hasNext()) {
            var batchSpec = PlanetJobBatch.make({values: batch});
            job.scheduleBatch(batchSpec);

            batch = [];
        }
    }
};

/**
 * 
 */
 function processBatch(batch, job, options){

    batch.values.forEach(function(oPlanet) {
        // TODO: Write the logic for processing 
    });
}