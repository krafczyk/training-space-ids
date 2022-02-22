def build(this):

    from sklearn.gaussian_process.kernels import ConstantKernel

    this.name = 'Constant'
    this.hyperParameters.push(this.ConstantValue)
    kernel = ConstantKernel(this.constantValue)

    this.pickledKernel = c3.PythonSerialization.serialize(obj=kernel)

    return