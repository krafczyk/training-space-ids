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

    c3.StagedFeatures.removeAll()

    df = pd.DataFrame()
    for model_id in ids:
        model = c3.GaussianProcessRegressionPipe.get(model_id)
        data_source_spec = c3.GPRDataSourceSpec.get(model.dataSourceSpec.id, "targetSpec")
        gstp_id = data_source_spec.targetSpec.filter.split(" == ")[1].replace('"', '')
        gstp = c3.GeoSurfaceTimePoint.get(gstp_id)
        pdf = c3.Dataset.toPandas(model.getFeatures())
        pdf["latitude"] = gstp.latitude
        pdf["longitude"] = gstp.longitude
        df = pd.concat([df,pdf], ignore_index=True)

    def row_to_dict(row):
        d = {}
        for col in row.index:
            d[col] = row[col]
        return d
        
    df_final = pd.DataFrame()
    df_final["features"] = df.apply(row_to_dict, axis=1)
    df_final["id"] = df_final.index
    output_records = df_final.to_dict(orient="records")
    c3.StagedFeatures.upsertBatch(objs=output_records)

    return 0