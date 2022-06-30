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

        // define the kernel
        var GPR_kernel = SklearnGPRKernelMatern.make({
            "lengthScale": [1.0],
            "nu": 0.5,
            "coefficient": 1.0
        }).build().kernel

        // define the technique
        var GPR_technique = GaussianProcessRegressionTechnique.make({
            "randomState": 42,
            "kernel": GPR_kernel
        });

        // define the features
        var featuresType = TypeRef.make({"typeName": "SimulationModelParameters"});
        var featuresSpec = FetchSpec.make({
            "limit": -1,
            "order": "id"
        });

        // define targets
        var targetType = TypeRef.make({"typeName": "Simulation3HourlyAODOutput"});
        var targetFilter = Filter.eq("geoSurfaceTimePoint.id", gstp.id);
        var targetSpec = FetchSpec.make({
            "limit": -1,
            "order": "simulationSample.id",
            "filter": targetFilter.toString()
        });

        // create pipe
        var pipeId = "GSTP_" + gstp.id;
        var GPR_pipe = GaussianProcessRegressionPipe.make({
            "technique": GPR_technique,
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
        y = y.extractColumns([options.targetName]);

        var GPR_pipe_trained = GPR_pipe.train(X, y);
        GPR_pipe_trained.upsert();

    });
}