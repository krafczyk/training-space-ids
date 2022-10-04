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
    
    df = pd.DataFrame()
    for model_id in ids:
        model = c3.GaussianProcessRegressionPipe.get(model_id)
        pdf = model.getTarget()
        df = pd.concat([df,pdf], ignore_index=True)

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
