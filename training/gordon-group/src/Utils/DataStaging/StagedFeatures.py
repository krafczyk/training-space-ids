def stageFromAODGPRModelIdsList(ids):
    """
    Given a list of GaussianProcessRegressionPipes trained with
    AOD data, stage the features for each model.

    Input:
        ids: list of model ids

    Return:
        int: zero if it worked, 1 if it failed
    """
    import pandas as pd

    # get data from dataSourceSpec one model
    model = c3.GaussianProcessRegressionPipe.get(ids[0], "dataSourceSpec")
    data_source_spec = c3.GPRDataSourceSpec.get(model.dataSourceSpec.id)
    excludeFeatures = data_source_spec.excludeFeatures
    featuresType = data_source_spec.featuresType.toType()
    inputTableC3 = featuresType.fetch(data_source_spec.featuresSpec).objs.toJson()
    inputTable = pd.DataFrame(inputTableC3)
    inputTable = inputTable.drop("version", axis=1)
    inputTable = inputTable.select_dtypes(["number"])
    if (excludeFeatures):
        inputTable.drop(columns=excludeFeatures, inplace=True)

    # get gstp coordinates from each model
    lats = []
    lons = []
    times = []
    for model_id in ids:
        model = c3.GaussianProcessRegressionPipe.get(model_id, "dataSourceSpec")
        data_source_spec = c3.GPRDataSourceSpec.get(model.dataSourceSpec.id, "targetSpec")
        gstp_id = data_source_spec.targetSpec.filter.split(" == ")[1].replace('"', '')
        gstp = c3.GeoSurfaceTimePoint.get(gstp_id)
        lats.append(gstp.latitude)
        lons.append(gstp.longitude)
        times.append(gstp.time)

    def row_to_dict(row):
        d = {}
        for col in row.index:
            d[col] = row[col]
        return d

    def add_coords(obj, lat, lon):
        obj["latitude"] = lat
        obj["longitude"] = lon
        return
    
    # build dataframe
    df_sim_par = pd.DataFrame()
    df_sim_par["features"] = inputTable.apply(row_to_dict, axis=1)

    df = pd.DataFrame()
    for i in range(len(lats)):
        df_to_add = df_sim_par.copy()
        df_to_add["features"].apply(add_coords, args=(lats[i], lons[i]))
        df = pd.concat([df,df_to_add], ignore_index=True)

    df["id"] = df.index
    output_records = df.to_dict(orient="records")
    c3.StagedFeatures.upsertBatch(objs=output_records)

    return 0