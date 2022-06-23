def getInputDataForSources(this, srcIds):
    """
    Fetch SimulationModelParameters, organize by SimulationSample, return C3 Dataset.
    """
    import pandas as pd

    features = c3.SimulationModelParameters.fetch({"limit": -1, "order": "id"}).objs.toJson()
    df = pd.DataFrame(features)
    df = df.sort_values(by = ["id"])
    X = df[df.columns[5:]]
    X = c3.Dataset.fromPython(X)
    
    return X

def getTargetDataForSources(this, srcIds):