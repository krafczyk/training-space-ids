def joinData(this, input):
    """
    input : geoSurfaceTimePoint
    """
    import pandas as pd

    # Collect the inputs
    inputTablePandas = pd.DataFrame(c3.SimulationModelParameters.fetch().objs.toJson())

    # Collect the outputs from the geoSpaceTimePoint
    s3haodFilter = c3.Filter().eq("geoSurfaceTimePoint", input)
    outputTableC3 = c3.Simulation3HourlyAODOutput.fetch(
        {"filter": s3haodFilter, "limit": -1}
    )
    outputTablePandas = pd.DataFrame(outputTableC3.objs.toJson())
    outputTablePandas["id"] = [row["id"] for row in outputTablePandas.simulationSample]

    # Join the outputs with the input table
    joinedData = pd.merge(
        inputTablePandas, # Input table -> DataFrame
        outputTablePandas,
        on="id",
        how="inner"
    )

    # Add identifier from the geoSurfaceTimePoint to each row
    nrows = joinedData.shape[0]
    joinedData["point"] = [input[k]["id"] for k in range(nrows)]

    return this
