def processBatch(batch, job, options):
    for file in batch.objs:
        file.download()