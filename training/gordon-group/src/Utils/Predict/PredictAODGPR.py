def makePredictionsJob(
    excFeats, gstpFilter, targetName, synthDataset, technique, batchSize
):
    """
    Dynamic map-reduce job to get predictions on synthDataset.
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
                    model_id = m["id"]
                    centered = m["technique"]["centerTarget"]
                    if centered:
                        center = m["trainedModel"].parameters["targetMean"].asfloat()
                    else:
                        center = 0
                    preds = m.process(synthDataset, computeStd=True)
                    values.append((preds, synthDataset, model_id, center))
                    

        return values

    map_lambda = c3.Lambda.fromPython(cassandra_mapper)
    reduce_lambda = c3.Lambda.fromPython(cassandra_reducer, runtime="gordon-ML_1_0_0")

    job_context = c3.MappObj(
        value={
            'excludeFeatures': excFeats,
            'targetName': targetName,
            'technique': technique,
            'syntheticDataset': synthDataset
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


def getPredictionsDataframeFromJob(job):
    """
    Iterates over job result and builds dataframe.
    """
    import pandas as pd
    import numpy as np

    predictions = []
    
    if job.status().status == "completed":
        for key, value in job.results().items():
            for subvalue in value:
                df_y = c3.Dataset.toPandas(subvalue[0])
                df_y[0] += subvalue[3]
                df_x = c3.Dataset.toPandas(subvalue[1])
                m_preds = pd.concat(
                    [df_x, df_y],
                    axis=1
                )
                m_preds["modelId"] = subvalue[2]
                predictions.append(m_preds)
                
        df = pd.concat(predictions, axis=0).reset_index(drop=True)
        return df
    else:
        return False