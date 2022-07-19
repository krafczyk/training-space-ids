def train(this, input, targetOutput, spec):
    """
    Performs Scikit-Learn's GaussianProcessRegressor's fit().
    https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html
    """
    from sklearn.gaussian_process import GaussianProcessRegressor

    technique = c3.GaussianProcessRegressionTechnique.get(this.technique.id)
    serializedKernel = c3.SklearnGPRKernel.get(technique.kernel.id)

    # get data
    X = c3.Dataset.toNumpy(dataset=input)
    y = c3.Dataset.toNumpy(dataset=targetOutput)

    # get kernel object from c3, make it python again
    kernel = c3.PythonSerialization.deserialize(serialized=serializedKernel.pickledKernel)

    # build and train GPR
    gp = GaussianProcessRegressor(kernel=kernel)
    gp.fit(X, y)

    this.trainedModel = c3.MLTrainedModelArtifact(model=c3.PythonSerialization.serialize(obj=gp))

    return this


def process(this, input, spec, computeStd=False, computeCov=False):
    """
    Performs Scikit-Learn's GaussianProcessRegressor's predict().
    https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html
    """
    import numpy as np

    # unpickle the model
    gp = c3.PythonSerialization.deserialize(serialized=this.trainedModel.model)

    # format data
    X = c3.Dataset.toNumpy(dataset=input)

    # get predictions: notice that cov and std simultaneously is not supported by Sklearn https://github.com/scikit-learn/scikit-learn/blob/baf0ea25d/sklearn/gaussian_process/_gpr.py#L327
    if computeStd and not computeCov:
        predictions, std = gp.predict(X, return_std=True)
        result = np.c_[predictions,std]

        return c3.Dataset.fromPython(pythonData=result)

    elif not computeStd and computeCov:
        predictions, cov = gp.predict(X, return_cov=True)
        result = np.concatenate((predictions,cov), axis=1)

        return c3.Dataset.fromPython(pythonData=result)

    else:
        predictions = gp.predict(X)

        return c3.Dataset.fromPython(pythonData=predictions)


def isProcessable(this):
    """"
    Guarantees that process() can only be called after train()
    """

    return this.isTrained()


def getFeatures(this):
    """
    Gets the features to train the GPR model.
    """
    import pandas as pd

    dataSourceSpec = c3.GPRDataSourceSpec.get(this.dataSourceSpec.id)

    featuresType = dataSourceSpec.featuresType.toType()
    inputTableC3 = featuresType.fetch(dataSourceSpec.featuresSpec).objs.toJson()
    inputTablePandas = pd.DataFrame(inputTableC3)
    inputTablePandas = inputTablePandas.drop("version", axis=1)

    # collect only the numeric fields
    inputTablePandas = inputTablePandas.select_dtypes(["number"])

    # drop ignored features
    if (dataSourceSpec.excludeFeatures):
        inputTablePandas.drop(columns=dataSourceSpec.excludeFeatures, inplace=True)

    return c3.Dataset.fromPython(inputTablePandas)


def getTarget(this):
    """
    Get the targets to train the GPR model.
    """
    import pandas as pd

    dataSourceSpec = c3.GPRDataSourceSpec.get(this.dataSourceSpec.id)

    targetType = dataSourceSpec.targetType.toType()
    outputTableC3 = targetType.fetch(dataSourceSpec.targetSpec).objs.toJson()
    outputTablePandas = pd.DataFrame(outputTableC3)
    outputTablePandas = outputTablePandas.drop("version", axis=1)

    # collect only the numeric fields
    outputTablePandas = outputTablePandas.select_dtypes(["number"])

    if dataSourceSpec.targetName == "all":
        outputTablePandas = pd.DataFrame(
            outputTablePandas.sum(axis=1),
            columns=[dataSourceSpec.targetName]
        )
    else:
        outputTablePandas = pd.DataFrame(outputTablePandas[dataSourceSpec.targetName])

    return c3.Dataset.fromPython(outputTablePandas)
