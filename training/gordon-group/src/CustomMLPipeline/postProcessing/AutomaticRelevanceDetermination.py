def train(this, input, targetOutput, spec):
    """
    Create structure where to store the kernel parameters

    input : GaussianProcessRegressionPipe
    """

    this.dtype = [('input', 'U35'), ('length_scale', float)]
    this.model = input

    return this


def process(this, input, spec):
    """
    Pair parameters with their lengthscales.

    input : list of parameter names
    """
    import pandas as pd
    import numpy as np

    model = c3.PythonSerialization.deserialize(serialized=this.trainedModel.model)
    learnedParameters = model.kernel_.get_params()
    lengthScales = learnedParameters["k2__length_scale"] # this feels a bit ugly but I'm not yet sure how to make this more generic
    parameterNames = input

    # Pair up parameters and their lengthscales
    pairedParameters = []
    for param in range(len(parameterNames)):
        pairedParameters.append((parameterNames[param], lengthScales[param]))

    # Make list sortable by applying dtype
    pairedParameters = np.array(pairedParameters, dtype=this.dtype)

    return c3.Dataset.fromPython(pythonData=pairedParameters)


def isProcessable(this):
    """"
    Guarantees that process() can only be called after train()
    """

    return this.isTrained()