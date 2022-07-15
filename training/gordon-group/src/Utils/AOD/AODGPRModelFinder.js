function getModel(excFeats, gstpId, targetName, technique) {

    // find the data source specs
    var gstpKey = "geoSurfaceTimePoint.id == '" + gstpId + "'";
    var filter = Filter.eq("featuresType.typeName", "SimulationModelParameters")
        .and().eq("targetType.typeName", "Simulation3HourlyAODOutput")
        .and().intersects("excludeFeatures", excFeats)
        .and().eq("targetName", targetName)
        .and().eq("targetSpec.filter", gstpKey);

    var sourceSpecIds = GPRDataSourceSpec.fetch({
        "filter": filter,
        "limit": -1,
        "include": "id"
    }).objs.map(obj => obj.id);

    // find the kernels
    filter = Filter.eq("pickledKernel", technique.kernel.pickledKernel);
    var kernelIds = SklearnGPRKernel.fetch({
        "filter": filter.value,
        "limit": -1,
        "include": "id"
    }).objs.map(obj => obj.id);

    // find the techniques
    filter = Filter.intersects("kernel.id", kernelIds);
    var techIds = GaussianProcessRegressionTechnique.fetch({
        "filter": filter.value,
        "limit": -1,
        "include": "id"
    }).objs.map(obj => obj.id);

    // now find the models
    filter = Filter.intersects("technique.id", techIds)
        .and().intersects("dataSourceSpec.id", sourceSpecIds);
    var pipeStream = GaussianProcessRegressionPipe.fetchObjStream({
        "filter": filter.value,
        "limit": -1
    });

    return pipeStream
}