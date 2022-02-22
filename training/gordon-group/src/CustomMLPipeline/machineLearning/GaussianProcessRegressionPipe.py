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