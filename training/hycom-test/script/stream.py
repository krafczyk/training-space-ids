# From https://community.c3.ai/t/how-to-stream-csv-files/4321/3
def streamFromS3(file, modelo = "Modelo_2020_02_27", geografia = "cat",**kwargs):
    logger.info("About to stream file "+ file)
    myfile=c3.S3File(url=c3.S3FileSystem().mounts()['DEFAULT'] +modelo+"/"+geografia+"/"+file)
    csv_string=StringIO(myfile.readString())
    mydf= pd.read_csv(csv_string,**kwargs)
    logger.info("File "+file+" streamed")
    return mydf