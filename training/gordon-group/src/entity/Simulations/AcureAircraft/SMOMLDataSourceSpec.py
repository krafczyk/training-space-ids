##
# Copyright (c) 2022, C3 AI DTI, Development Operations Team
# All rights reserved. License: https://github.com/c3aidti/.github
##
def getInputDataForSources(this, srcIds):
    """
    Implementation of...
    """
    import pandas as pd
    #from sklearn.model_selection import train_test_split

    # fetch features
    features = c3.SimulationModelParameters.fetch({"limit": -1, "order": "id"}).objs.toJson()
    df = pd.DataFrame(features)
    X = df[df.columns[5:]]
    X = df.sample(frac=this.leaveBehindRatio, random_state=this.randomSeed)

    # cast it into 
    X = c3.Dataset.fromPython(X)

    return 0
   # return [X,y]