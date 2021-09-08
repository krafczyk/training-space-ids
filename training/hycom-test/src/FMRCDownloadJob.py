def processBatch(batch, job, options):
    for file in batch:
        file.download()