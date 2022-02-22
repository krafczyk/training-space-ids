def build(this):

    from sklearn.gaussian_process.kernel import ConstantKernel

    this.name = 'Constant'
    kernel = ConstantKernel(this.constantValue)

    this.pickledKernel = c3.PythonSerialization.serialize(obj=kernel)

    return