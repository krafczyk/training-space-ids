/**
 * @param {int} batch The batch number being processed
 * @param {GeoSurfaceTimePoint[]} objs Object instances being processed
 * @param {MapReduce} job The job instance
 * @returns {Map} A map with models for each batch
 */
function map(batch, objs, job) {
    var dict = {};
    var models = objs.forEach(function (obj) {
        AODGPRModelFinder.getPipe(
            job.context.excludeFeatures, 
            obj.id,
            job.context.targetName,
            job.context.technique);
    });
    dict[batch] = models;
    return dict;
}
