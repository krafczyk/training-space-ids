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

    # open file
    sample = c3.NetCDFUtil.openFile(this.file.url)
    
    # cast it to dataframe
    df = pd.DataFrame()
    df['time'] = sample.variables['time'][:]
    df['longitude'] = sample.variables['longitude'][:]
    df['latitude'] = sample.variables['latitude'][:]
    df['mass_BC_acc'] = sample.variables['mass_fraction_of_black_carbon_in_soluble_accumulation_mode_dry_aerosol_in_air'][:]
    df['mass_BC_Ait'] = sample.variables['mass_fraction_of_black_carbon_in_soluble_aitken_mode_dry_aerosol_in_air'][:] 
    df['mass_BC_Aitins'] = sample.variables['mass_fraction_of_black_carbon_in_insoluble_aitken_mode_dry_aerosol_in_air'][:] 
    df['mass_BC_cor'] = sample.variables['mass_fraction_of_black_carbon_in_soluble_coarse_mode_dry_aerosol_in_air'][:] 
    df['mass_OC_acc'] = sample.variables['mass_fraction_of_particulate_organic_matter_in_soluble_accumulation_mode_dry_aerosol_in_air'][:]
    df['mass_OC_Ait'] = sample.variables['mass_fraction_of_particulate_organic_matter_in_soluble_aitken_mode_dry_aerosol_in_air'][:] 
    df['mass_OC_Aitins'] = sample.variables['mass_fraction_of_particulate_organic_matter_in_insoluble_aitken_mode_dry_aerosol_in_air'][:] 
    df['mass_OC_cor'] = sample.variables['mass_fraction_of_particulate_organic_matter_in_soluble_coarse_mode_dry_aerosol_in_air'][:] 
    # a little gymnastic to get Datetime objs
    zero_time = datetime(1970,1,1,0,0)
    transformed_times = []
    for time in df['time']:
        target_time = zero_time + timedelta(hours=time)
        transformed_times.append(target_time)
    df['datetime'] = transformed_times
    df.drop(columns=['time'], inplace=True)

    parent_id = "SMOS_" + this.simulationSample.id
    df['parent'] = parent_id

    now_time = datetime.now()
    diff_time = (now_time - zero_time)
    versionTag= -1 * diff_time.total_seconds()
    df['versionTag'] = versionTag

#    output_records = df.to_dict(orient="records")
    # create list of SimulationModelOutput objs
    output_records = [
        c3.SimulationModelOutput(**{
            'longitude': df['longitude'].iloc[i],
            'latitude': df['latitude'].iloc[i],
            'mass_BC_acc': df['mass_BC_acc'].iloc[i],
            'mass_BC_Ait': df['mass_BC_Ait'].iloc[i],
            'mass_BC_Aitins': df['mass_BC_Aitins'].iloc[i],
            'mass_BC_cor': df['mass_BC_cor'].iloc[i],
            'mass_OC_acc': df['mass_OC_acc'].iloc[i],
            'mass_OC_Ait': df['mass_OC_Ait'].iloc[i],
            'mass_OC_Aitins': df['mass_OC_Aitins'].iloc[i],
            'mass_OC_cor': df['mass_OC_cor'].iloc[i],
            'start': df['datetime'].iloc[i],
            'parent': parent_id,
            'dataVersion': versionTag
        })
        for i in range(len(df))
    ]

    # upsert this batch
    c3.SimulationModelOutput.upsertBatch(output_records)

    this.processed = True
    c3.SimulationOutputFile.merge(this)
    return True
    