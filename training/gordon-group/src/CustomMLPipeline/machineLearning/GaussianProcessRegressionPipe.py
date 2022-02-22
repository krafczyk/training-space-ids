def train(this, input, targetOutput, spec):
    """
    Performs Scikit-Learn's GaussianProcessRegressor's fit().
    https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html
    """
    from sklearn.gaussian_process import GaussianProcessRegressor

    # get data
    X = c3.Dataset.toNumpy(dataset=input)
    y = c3.Dataset.toNumpy(dataset=targetOutput).flatten()

    # build and train GPR
    gp = GaussianProcessRegressor()
    gp.fit(X, y)

    # pickle model
    this.trainedModel = c3.MLTrainedModelArtifact(model=c3.PythonSerialization.serialize(obj=gp))

    return this


def process(this, input, spec):
    """
    Performs Scikit-Learn's GaussianProcessRegressor's predict().
    https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html
    """
    # unpickle the model
    gp = c3.PythonSerialization.deserialize(serialized=this.trainedModel.model)

    # format data
    X = c3.Dataset.toNumpy(dataset=input)

    return c3.Dataset.fromPython(pythonData=gp.predict(X))


def isProcessable(this):
    """"
    Guarantees that process() can only be called after train()
    """

    return this.isTrained()
