/**
 * RemoveAODData.js
 * Implementation of RemoveAODData.c3typ
 * @param {RemoveAODData} job
 * @param {UpsertAODDataOptions} options
 */
 function doStart(job, options) {

    var deltaTime = Math.abs(options.finalDate - options.initialDate);
    var nBatches;
    var batches = [];
    var hour = 1000*60*60;
    var day = hour*24;
    if (options.timeGranularity == 'HOUR') {
        nBatches = Math.ceil(deltaTime / hour);
        for (var i = 0; i < nBatches; i++) {
            var date = options.initialDate + i*hour;
            var filter = Filter.ge("geoSurfaceTimePoint.time", date).and().lt("geoSurfaceTimePoint.time", date + hour);
            var spec = FetchSpec.make({include: "[id]", limit: options.limit, 
                filter: filter
            });
            batches.push(spec);
        }
    }
    else if (options.timeGranularity == 'DAY') {
        nBatches = Math.ceil(deltaTime / day);
        for (var i = 0; i < nBatches; i++) {
            var date = options.initialDate + i*day;
            var filter = Filter.ge("geoSurfaceTimePoint.time", date).and().lt("geoSurfaceTimePoint.time", date + day).toString();
            var spec = FetchSpec.make({include: "[id]", limit: options.limit, 
                filter: filter
            });
            batches.push(spec);
        }
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
    var objects = Simulation3HourlyAODOutputAllRef(spec=batch);
    Simulation3HourlyAODOutputAllRef.removeBatch(objects);
}