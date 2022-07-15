/**
 * @param {int} batch The batch number being processed
 * @param {GeoSurfaceTimePoint[]} objs Object instances being processed
 * @param {MapReduce} job The job instance
 * @returns {Map} A map with models for each batch
 */
function map(batch, objs, job) {
    var dict = {};
    var models = objs.forEach(function (obj) {
        AODModelFinder.getPipe(
            job.context.excludeFeatures, 
            obj.id,
            job.context.targetName,
            job.context.technique);
    });
    dict[batch] = models;
    return dict;
}

/**
 * @param {string} outKey Output key this function is being called for
 * @param {int[]} interValues Intermediate counts for the same word
 * @param {MapReduce} job The job instance
 * @returns {int[]} A single value array with the number of times a word occurred
 */
function reduce(outKey, interValues, job) {
    var values = [];

    for (var i = 0; i < interValues.length; i++) {
        var iv = interValues[i];
        for (var j = 0; j < iv.length; j++) {
            var val = iv[j];
            var pickledModel = val["trainedModel"]["model"];
            var model = PythonSerialization.deserialize(serialized=pickledModel);
            var hp = model.kernel_.get_params()['k2__length_scale'];
            var model_id = val["id"];
            values.append([hp, model_id]);
        };
    };

    return values;
}