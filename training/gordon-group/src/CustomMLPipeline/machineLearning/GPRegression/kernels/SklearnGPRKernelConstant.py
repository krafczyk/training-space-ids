def build(this):

    from sklearn.gaussian_process.kernels import ConstantKernel
    import numpy as np

#    this.kernel.name = 'Constant'
#    hyperPars = [this.constantValue]
#    this.kernel.hyperParameters = hyperPars
#    sklKernel = ConstantKernel(this.constantValue)
#
#    this.kernel.pickledKernel = c3.PythonSerialization.serialize(obj=sklKernel)

    sklKernel = ConstantKernel(this.constantValue)

    kernel_pickled = c3.PythonSerialization.serialize(obj=sklKernel)
    kernel_name = 'Constant'
    kernel_hyperParameters = [this.constantValue]

    this.kernel = c3.SklearnGPRKernel({
        name=kernel_name,
        hyperParameters=kernel_hyperParameters,
        pickledKernel=kernel_pickled
    })

    return this