def upsertORACLESData(this):
    """
    Function to Open files in the ObservationOutputFile table and then populate ObservationOutput data.
    
    - Arguments:
        -this: an instance of ObservationOutputFile

    - Returns:
        -bool: True if file was processed, false if file has already been processed
    """
    from datetime import datetime, timedelta
    import pandas as pd

    # open file
    sample = c3.NetCDFUtil.openFile(this.file.url)
    
    # cast it to dataframe
    df = pd.DataFrame()
    df['time'] = sample.variables['time'][:]
    df['time'] = pd.to_datetime(df['time'],unit='s')
    df['longitude'] = sample.variables['Longitude'][:]
    df['latitude'] = sample.variables['Latitude'][:]
    df['altitude'] = sample.variables['GPS_Altitude'][:]
    df['total_BC'] = sample.variables['rBC_massConc'][:]
    

    obsSet = c3.ObservationSet.get(this.observationSet.id)
    parent_id = "OOS_SetName_" + obsSet.name + "_Ver_" + obsSet.versionTag
    df['parent'] = parent_id

    zero_time = datetime(1970,1,1,0,0)
    now_time = datetime.now()
    diff_time = (now_time - zero_time)
    versionTag= -1 * diff_time.total_seconds()
    df['dataVersion'] = versionTag

    output_records = df.to_dict(orient="records")

    # upsert this batch
    c3.ObservationOutput.upsertBatch(objs=output_records)

    this.processed = True
    c3.ObservationOutputFile.merge(this)
    return True