def processBatch(batch, job, options):
    for file in batch.values:
        file.download()