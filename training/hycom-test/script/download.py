def downloadToS3External(srcUrl, fileName, s3_folder):
    r = requests.get(srcUrl)
    tmp_path = "/tmp/" + fileName
    with open(tmp_path, 'wb') as f:
        f.write(r.content)
    c3.Client.uploadLocalClientFiles(tmp_path, s3_folder, {"peekForMetadata": True})
    logger.info("file {} downloaded to {}".format(fileName, s3_folder + fileName))
    os.remove(tmp_path)
    return s3_folder + fileName