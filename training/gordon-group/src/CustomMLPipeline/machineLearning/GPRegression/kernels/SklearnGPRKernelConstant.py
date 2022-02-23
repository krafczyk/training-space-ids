def build(this):

    from sklearn.gaussian_process.kernels import ConstantKernel
    import numpy as np

    this.name = 'Constant'
    hyperPars = [this.constantValue]
    this.hyperParameters = hyperPars
    kernel = ConstantKernel(this.constantValue)

    this.pickledKernel = c3.PythonSerialization.serialize(obj=kernel)

    return this