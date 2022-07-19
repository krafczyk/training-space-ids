def extractLearnedParametersJob(excFeats, gstpFilter, targetName, technique, batchSize):
    """
    Dynamic map-reduce job to extract learned hyper parameters.
    """
    def cassandra_mapper(batch, objs, job):
        models = []
        for obj in objs:
            model = c3.AODGPRModelFinder.getPipe(
                job.context.value["excludeFeatures"],
                obj.id,
                job.context.value["targetName"],
                job.context.value["technique"]
            )
            models.append(model)
        
        return {batch: models}

    def cassandra_reducer(key, interValues, job):
        values = []
        for iv in interValues:
            for val in iv:
                for m in val:
                    pickledModel = m["trainedModel"]["model"]
                    model = c3.PythonSerialization.deserialize(serialized=pickledModel)
                    hp = model.kernel_.get_params()['k2__length_scale']
                    model_id = m["id"]
                    values.append((hp, model_id))

        return values

    map_lambda = c3.Lambda.fromPython(cassandra_mapper)
    reduce_lambda = c3.Lambda.fromPython(cassandra_reducer, runtime="gordon-ML_1_0_0")

    job_context = c3.MappObj(
        value={
            'excludeFeatures': excFeats,
            'targetName': targetName,
            'technique': technique
        }
    )
    job = c3.DynMapReduce.startFromSpec(
        c3.DynMapReduceSpec(
            targetType="GeoSurfaceTimePoint",       
            filter=gstpFilter, 
            mapLambda=map_lambda,
            reduceLambda=reduce_lambda,
            batchSize=batchSize,
            context=job_context
        )
    )

    return job


def getDataframeFromJob(job):
    """
    Iterates over job result and builds dataframe.
    """
    import pandas as pd
    import numpy as np

    lengthScales = []
    ids = []
    if job.status().status == "completed":
        for key, value in job.results().items():
            for subvalue in value:
                ls = np.array(subvalue[0]).astype(float)
                model_id = np.array([subvalue[1]]).astype(str)
                lengthScales.append(ls)
                ids.append(model_id[0])
                
        df = pd.DataFrame(lengthScales)
        df["modelId"] = ids
        return df
    else:
        return False