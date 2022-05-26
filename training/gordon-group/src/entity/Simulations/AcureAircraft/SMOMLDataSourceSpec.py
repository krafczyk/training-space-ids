##
# Copyright (c) 2022, C3 AI DTI, Development Operations Team
# All rights reserved. License: https://github.com/c3aidti/.github
##
def getInputDataForSources(this, srcIds):
    """
    Implementation to get Features, viz. SimulationModelParameters
    """
    import pandas as pd
    #from sklearn.model_selection import train_test_split

    # fetch features
    features = c3.SimulationModelParameters.fetch({"limit": -1, "order": "id"}).objs.toJson()
    df = pd.DataFrame(features)
    df = df.sort_values(by = ["id"])
    X = df[df.columns[5:]]
    frac = (1.0 - this.leaveBehindRatio)
    X = X.sample(frac=frac, random_state=this.randomSeed)

    # cast it into 
    X = c3.Dataset.fromPython(X)

    return X



def getTargetDataForSources(this, srcIds):
    """
    Implementation to get Targets, viz. SimulationModelOutputSeries
    """
    import pandas as pd
    
    parameters = c3.SimulationModelParameters.fetch({"include": "id"}).objs
    parameters = parameters.toJson()
    df = pd.DataFrame(parameters)
    df = df.sort_values(by = ["id"])
    simulations = pd.DataFrame(df['id'])
    frac = (1.0 - this.leaveBehindRatio)
    simulations = simulations.sample(frac=frac, random_state=this.randomSeed)


    metric_name = "Average_" + this.targetName + "_SimulationSample" 
    metric_descr = "Calculates average of " + this.targetName + " for all SimulationSamples"
    metric_expr = "avg(avg(normalized.data." + this.targetName + "))"
    metric = c3.SimpleMetric(id = metric_name,
        name = metric_name,
        description = metric_descr,
        srcType = "SimulationSample",
        path = "output", 
        expression = metric_expr
    )

    spec = c3.EvalMetricsSpec(
        ids = simulations['id'],
        expressions = [metric_name],
        start = this.timestamp,
        end = this.timestamp,
        interval = "SECOND" 
    )

    evalMetricsResult = c3.SimulationSample.evalMetricsWithMetadata(
        spec=spec,
        overrideMetrics=[metric]
    )

    y = c3.EvalMetricsResult.toPandas(result=evalMetricsResult)
    y = c3.Dataset.fromPython(y)

    return y