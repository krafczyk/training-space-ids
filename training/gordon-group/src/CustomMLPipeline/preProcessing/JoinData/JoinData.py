def train(this, input, spec):
    """
    Get a table which lists the inputs to be considered for GP regression. Some
    inputs are assumed a priori to be irrelevant (e.g. ones with 'carb' or 'ems'
    in the name), but we do not select these out in this pipe.

    input : c3.FetchResult<SimulationModelParameters>
        Model parameter table, i.e. the result of
        c3.SimulationModelParameters.fetch()
    """
    this.inputTable = input

    return this


def process(this, input, spec):
    """
    Define a geoSpaceTimePoint for the dataset which is desired and input it
    here to filter out data at that GSTP. Then join it with the input table.

    input : c3.FetchResult<GeoSurfaceTimePoint>
        A C3 type defined for specifying the latitude-longitude-time range for
        which all simulation ensemble members' outputs are desired.
    """
    import pandas as pd

    includeTotal = this.technique.includeTotal
    this.GSTP = input

    # Collect the outputs from the geoSpaceTimePoint
    s3haodFilter = c3.Filter().eq("geoSurfaceTimePoint", this.GSTP)
    outputTableC3 = c3.Simulation3HourlyAODOutput.fetch(
        {"filter": s3haodFilter, "limit": -1}
    )
    outputTablePandas = pd.DataFrame(outputTableC3.objs.toJson())
    outputTablePandas["id"] = [row["id"] for row in outputTablePandas.simulationSample]
    this.outputTable = outputTablePandas

    # Compute total column
    # if includeTotal:

    # Join the outputs with the input table
    joinedData = pd.merge(
        pd.DataFrame(this.inputTable.objs.toJson()), # Input table -> DataFrame
        this.outputTable,
        on="id",
        how="inner"
    )

    nrows = joinedData.shape[0]
    joinedData["point"] = [this.GSTP[k]["id"] for k in range(nrows)]

    return c3.Dataset.fromPython(pythonData=joinedData)


def isProcessable(this):
    """"
    Guarantees that process() can only be called after train()
    """

    return this.isTrained()