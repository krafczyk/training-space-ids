def getInputDataForSources(this, srcIds):
    """
    Gets the features to train the model from SimulationModelParameters.
    """
    import pandas as pd

    # Collect the inputs and sort by SimulationSample
    inputTablePandas = pd.DataFrame(c3.SimulationModelParameters.fetch({"limit": -1, "order": "id"}).objs.toJson())
    inputTablePandas = inputTablePandas.drop("version", axis=1)

    return c3.Dataset.fromPython(inputTablePandas.select_dtypes(["number"]))


#def combineInputDataObjects(this, dataObjs):
#    """
#    dataObjs : geoSurfaceTimePoint
#    """
#
#    # Get input table
#    inputTablePandas = c3.Dataset.toPandas(this.getInputDataForSources())
#
#    # Collect the outputs from the geoSpaceTimePoint
#    s3haodFilter = c3.Filter().eq("geoSurfaceTimePoint", dataObjs)
#    outputTableC3 = c3.Simulation3HourlyAODOutput.fetch(
#        {"filter": s3haodFilter, "limit": -1}
#    )
#    outputTablePandas = pd.DataFrame(outputTableC3.objs.toJson())
#    outputTablePandas["simID"] = [int(row["id"]) for row in outputTablePandas.simulationSample]
#
#    # Join the outputs with the input table
#    joinedData = pd.merge(
#        inputTablePandas,
#        outputTablePandas,
#        on="simID",
#        how="inner"
#    )
#
#    # Add identifier from the geoSurfaceTimePoint to each row
#    nrows = joinedData.shape[0]
#    joinedData["point"] = [dataObjs[k]["id"] for k in range(nrows)]
#
#    return joinedData
#