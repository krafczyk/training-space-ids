def stageFromAODGPRModelIdsList(ids):
    """
    Given a list of GaussianProcessRegressionPipes trained with
    AOD data, stage the targets for each model.

    Input:
        ids: list of model ids

    Return:
        int: zero if it worked, 1 if it failed
    """
    import pandas as pd

    c3.StagedTargets.removeAll()

    model = c3.GaussianProcessRegressionPipe.get(ids[0], "dataSourceSpec")
    data_source_spec = c3.GPRDataSourceSpec.get(model.dataSourceSpec.id)
    target_type = data_source_spec.targetType.toType()

    df = pd.DataFrame()

    for model_id in ids:
        model = c3.GaussianProcessRegressionPipe.get(model_id, "dataSourceSpec")
        data_source_spec = c3.GPRDataSourceSpec.get(model.dataSourceSpec.id)
        outputC3 = target_type.fetch(data_source_spec.targetSpec).objs.toJson()
        output = pd.DataFrame(outputC3)
        output = output.drop("version", axis=1)
        if data_source_spec.targetName == "all":
            output = pd.DataFrame(
                output.sum(axis=1),
                columns=[data_source_spec.targetName]
            )
        else:
            output = pd.DataFrame(output[data_source_spec.targetName])

        df = pd.concat([df, output], ignore_index=True)

    def row_to_dict(row):
        d = {}
        for col in row.index:
            d[col] = row[col]
        return d

    df_final = pd.DataFrame()
    df_final["targets"] = df.apply(row_to_dict, axis=1)
    df_final["id"] = df_final.index

    output_records = df_final.to_dict(orient="records")
    c3.StagedTargets.upsertBatch(objs=output_records)

    return 0
