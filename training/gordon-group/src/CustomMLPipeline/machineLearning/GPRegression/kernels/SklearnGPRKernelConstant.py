def build(this):

    from sklearn.gaussian_process.kernels import ConstantKernel
    import numpy as np

    this.kernel.name = 'Constant'
    hyperPars = [this.constantValue]
    this.kernel.hyperParameters = hyperPars
    sklKernel = ConstantKernel(this.constantValue)

    this.kernel.pickledKernel = c3.PythonSerialization.serialize(obj=sklKernel)

    return this