/**
* Copyright (c) 2022, C3 AI DTI, Development Operations Team
* All rights reserved. License: https://github.com/c3aidti/.github
**/
/**
 * Implementation of AODGaussianMLTrainingJob
 * @param {AODGaussianMLTrainingJob} job
 * @param {AODGaussianMLTrainingJobOptions} options
 */
 function doStart(job, options) {
    var batch = [];

    var gstps = GeoSurfaceTimePoint.fetchObjStream({
        filter: options.gstpFilter,
        limit: -1
    });

    while(gstps.hasNext()) {
        batch.push(gstps.next());

        if (batch.length >= options.batchSize || !gstps.hasNext()) {
            var batchSpec = AODGaussianMLTrainingJobBatch.make({values: batch});
            job.scheduleBatch(batchSpec);
            
            batch = [];
        }
    }
}


/**
 * Implementation of what to do in each batch
 * @param {AODGaussianMLTrainingJobBatch} batch
 * @param {AODGaussianMLTrainingJob} job
 * @param {AODGaussianMLTrainingJobOptions} options
 */
function processBatch(batch, job, options) {
    batch.values.forEach(function(gstp) {

        // define targets
        var targetType = TypeRef.make({"typeName": "Simulation3HourlyAODOutput"});
        var targetFilter = Filter.eq("geoSurfaceTimePoint.id", gstp.id);
        var targetSpec = FetchSpec.make({
            "limit": -1,
            "order": "simulationSample.id",
            "filter": targetFilter.toString()
        });

        // find the simulations
        var simulationsSpec = FetchSpec.make({
            "limit": -1,
            "order": "simulationSample.id",
            "filter": targetFilter.toString(),
            "include": "simulationSample"
        });
        var samples = targetType.fetch(simulationsSpec).objs
        var simIds = []
        for(var i = 0; i < samples.length; i++) {
            simIds.push(samples[i].simulationSample.id);
        }

        var allSamples = featuresType.fetch({
            "limit": -1,
            "order": "id",
            "include": "id"
        })
        var allSimIds = []
        for(var i = 0; i < allSamples.length; i++) {
            simIds.push(allSamples[i].id);
        }
        var excludeIds = []
        for(var i = 0; i < allSamples.length; i++) {
            if(!simIds.includes(allSimIds[i])) {
                excludeIds.push(allSimIds[i]);
            }
        }

        // define the features
        var featuresFilter = Filter.not().intersects("id", excludeIds);
        var featuresType = TypeRef.make({"typeName": "SimulationModelParameters"});
        var featuresSpec = FetchSpec.make({
            "limit": -1,
            "order": "id",
            "filter": featuresFilter
        });

        // create pipe
        var pipeId = "GSTP_" + gstp.id + "_" + options.targetName;
        var GPR_pipe = GaussianProcessRegressionPipe.make({
            "technique": options.gprTechnique,
            "featuresType": featuresType,
            "featuresSpec": featuresSpec,
            "targetType": targetType,
            "targetSpec": targetSpec,
            "targetName": options.targetName,
            "id": pipeId
        });

        // get targets
        var X = GPR_pipe.getFeatures();
        var y = GPR_pipe.getTarget();
        if (options.targetName === "all") {
            var sum = new Array(y.shape[0]).fill(0);
            for(var i=0; i<y.shape[1]; i++) {
                var colName = y.indices[1][i];
                var col = y.extractColumns([colName]).m_data;
                sum = sum.map(function (val, idx) {
                    return val + col[idx];
                });
            }
            y.indices[1][0] = "all";
            col = y.extractColumns(["all"]);
            col.m_data = sum;
            y = col;
        }
        y = y.extractColumns([options.targetName]);

        var GPR_pipe_trained = GPR_pipe.train(X, y);
        GPR_pipe_trained.upsert();

    });
}