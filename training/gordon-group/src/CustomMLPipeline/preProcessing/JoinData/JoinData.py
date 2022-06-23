def getInputDataForSources(this, srcIds):
    """
    Gets the features to train the model from SimulationModelParameters.
    """
    import pandas as pd

    # Collect the inputs and sort by SimulationSample
    inputTablePandas = pd.DataFrame(c3.SimulationModelParameters.fetch({"limit": -1, "order": "id"}).objs.toJson())
    inputTablePandas = inputTablePandas.drop("version", axis=1)

    return c3.Dataset.fromPython(inputTablePandas.select_dtypes(["number"]))


def getTargetDataForSources(this, srcIds):
    """
    dataObjs : geoSurfaceTimePoint
    """
    import pandas as pd

    gstp_id = srcIds[0]
    s3haodFilter = c3.Filter().eq("geoSurfaceTimePoint.id", gstp_id)
    outputTableC3 = c3.Simulation3HourlyAODOutput.fetch({
        "filter": s3haodFilter, 
        "limit": -1, 
        "order": "simulationSample.id"
        }
    )
    outputTablePandas = pd.DataFrame(outputTableC3.objs.toJson())
    outputTablePandas = outputTablePandas.drop("version", axis=1)
    ### simplifcation
    df = pd.DataFrame(outputTablePandas.select_dtypes(["number"])["dust"])

    return c3.Dataset.fromPython(df)

