def train(this, input, targetOutput, spec):
    """
    Performs Scikit-Learn's PCA.
    https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
    """
    from sklearn.decomposition import PCA

    # get number of PCA components
    nComps = this.technique.nComponents
    
    # cast features into pandas df
    data = c3.Dataset.toPandas(dataset=input)

    # call pca
    pca = PCA(n_components=nComps)
    data = pca.fit_transform(data)

    # serialize this training
    this.trainedModel = c3.MLTrainedModelArtifact(model=c3.PythonSerialization.serialize(obj=data))

    return this