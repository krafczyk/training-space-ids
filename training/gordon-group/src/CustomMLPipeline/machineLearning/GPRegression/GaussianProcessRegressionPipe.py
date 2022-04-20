def train(this, input, targetOutput, spec):
    """
    Performs Scikit-Learn's GaussianProcessRegressor's fit().
    https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html
    """
    from sklearn.gaussian_process import GaussianProcessRegressor

    # get data
    X = c3.Dataset.toNumpy(dataset=input)
    y = c3.Dataset.toNumpy(dataset=targetOutput).flatten()

    # get kernel object from c3, make it python again
    kernel = c3.PythonSerialization.deserialize(serialized=this.technique.kernel.pickledKernel)

    # build and train GPR
    gp = GaussianProcessRegressor(kernel=kernel)
    gp.fit(X, y)

    # this step for updating the kernel parameters is written specifically for the Matern parameters
    # Bruno - we may want to do this outside this method
    # since this one is supposed to work regardless the kernel choice
    #if this.kernel.kernel_name is 'Matern':
#
    #    # record kernel parameters now that they are fitted
    #    fit_params = gp.kernel_.get_params()
#
    #    updated_hyperParameters = c3.c3Make(
    #        "map<string, double>", {
    #            "lengthScale": list(fit_params['k2__length_scale']),
    #            "coefficient": fit_params['k1'],
    #            "nu": fit_params['k2__nu']
    #        }
    #    )
#
    #    # restate the kernel using the fitted parameters
    #    this.kernel = c3.SklearnGPRKernel(
    #        name=this.kernel.kernel_name,
    #        hyperParameters=updated_hyperParameters,
    #        pickledKernel=this.kernel.kernel_pickled
    #    )

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
