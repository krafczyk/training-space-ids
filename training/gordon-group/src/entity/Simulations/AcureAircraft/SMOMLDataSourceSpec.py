##
# Copyright (c) 2022, C3 AI DTI, Development Operations Team
# All rights reserved. License: https://github.com/c3aidti/.github
##
def getInputDataForSources(this, srcIds):
    """
    Implementation of...
    """
    import pandas as pd
    from sklearn.model_selection import train_test_split

    # fetch features
    features = c3.SimulationModelParameters.fetch({"limit": -1}).objs.toJson()
    df = pd.DataFrame(features)
    simulationSamples = pd.DataFrame(df['id'])
    X = df[df.columns[5:]]

    # now grab the targets
   # metricName = "Average_" + this.targetName + "_SimulationSample"
   # metricDescr = "Calculates average of " + this.targetName + " for a given set of SimulationSample"
   # metricExpr = "avg(avg(normalized.data." + this.targetName + "))"
   # metric = c3.SimpleMetric(
   #     id = metricName,
   #     name = metricName,
   #     description = metricDescr,
   #     srcType = "SimulationSample",
   #     path = "output",
   #     expression = metricExpr
   # )
   # spec = c3.EvalMetricsSpec(
   #     ids = simulationSamples['id'],
   #     expressions = [metricName],
   #     start = this.timestamp,
   #     end = this.timestamp,
   #     interval = 'SECOND'
   # )
   # evalMetricsResult = c3.SimulationSample.evalMetricsWithMetadata(
   #     spec = spec,
   #     overrideMetrics = [metric]
   # )
   # y = c3.EvalMetricsResult.toPandas(result=evalMetricsResult)
   # 
    X = c3.Dataset.fromPython(X)
    #y = c3.Dataset.fromPython(y)

    return X
   # return [X,y]