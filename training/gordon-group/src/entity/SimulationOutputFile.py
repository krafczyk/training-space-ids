def upsertData(this):
    """
    Function to Open files in the SimulationOutputFile table and then populate SimulationModelOutput and SimulationModelOutputSeries data.
    
    - Arguments:
        -this: an instance of SimulationOutputFile

    - Returns:
        -bool: True if file was processed, false if file has already been processed
    """
    from datetime import datetime, timedelta
    import pandas as pd

    if(this.processed == False):
        # open file
        sample = c3.NetCDFUtil.openFile(this.file.url)
        
        # cast it to dataframe
        df = pd.DataFrame()
        df['time'] = sample.variables['time'][:]
        df['longitude'] = sample.variables['longitude'][:]
        df['latitude'] = sample.variables['latitude'][:]
        df['propertyX'] = sample.variables['mass_fraction_of_black_carbon_in_soluble_accumulation_mode_dry_aerosol_in_air'][:]

        # a little gymnastic to get Datetime objs
        zero_time = datetime(1970,1,1,0,0)
        transformed_times = []
        for time in df['time']:
            target_time = zero_time + timedelta(hours=time)
            transformed_times.append(target_time)
        df['datetime'] = transformed_times
        df.drop(columns=['time'], inplace=True)

        # create list of SimulationModelOutput objs
        output_records = [
            c3.SimulationModelOutput(**{
                'longitude': df['longitude'].iloc[i],
                'latitude': df['latitude'].iloc[i],
                'propertyX': df['propertyX'].iloc[i],
                'start': df['datetime'].iloc[i],
                'parent': this.simulationSample.id
            })
            for i in range(len(df))
        ]

        # upsert this batch
        c3.SimulationModelOutput.upsertBatch(output_records)

        this.processed = True
        c3.SimulationOutputFile.merge(this)
        return True
    else:
        return False
    