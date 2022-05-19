def upsertAcureAircraftData(this):
    """
    Function to Open files in the SimulationOutputFile table with acure-aircraft container and then populate SimulationModelOutput and SimulationModelOutputSeries data.
    
    - Arguments:
        -this: an instance of SimulationOutputFile

    - Returns:
        -bool: True if file was processed, false if file has already been processed or if container type does not match.
    """
    from datetime import datetime, timedelta
    import pandas as pd

    # verify file container
    if(this.container == 'acure-aircraft'):
        #open file
        sample = c3.NetCDFUtil.openFile(this.file.url)
    
        # cast it to dataframe
        df = pd.DataFrame()
        df['time'] = sample.variables['time'][:]
        df['longitude'] = sample.variables['longitude'][:]
        df['latitude'] = sample.variables['latitude'][:]
        df['altitude'] = sample.variables['altitude'][:]
        df['model_level_number'] = sample.variables['model_level_number'][:]
        df['air_potential_temperature']= sample.variables['air_potential_temperature'][:]
        df['air_pressure'] = sample.variables['air_pressure'][:]
        df['cloud_flag'] = sample.variables['m01s38i478'][:]
        df['cdnc_x_cloud_flag'] = sample.variables['m01s38i479'][:]
        df['ambient_extinction_550'] = sample.variables['m01s02i530_550nm'][:]
        df['ambient_scattering_550'] = sample.variables['m01s02i532_550nm'][:]
        df['num_nuc'] = sample.variables['number_of_particles_per_air_molecule_of_soluble_nucleation_mode_aerosol_in_air'][:]
        df['num_Ait'] = sample.variables['number_of_particles_per_air_molecule_of_soluble_aitken_mode_aerosol_in_air'][:]
        df['num_acc'] = sample.variables['number_of_particles_per_air_molecule_of_soluble_accumulation_mode_aerosol_in_air'][:]
        df['num_cor'] = sample.variables['number_of_particles_per_air_molecule_of_soluble_coarse_mode_aerosol_in_air'][:]
        df['num_Aitins'] = sample.variables['number_of_particles_per_air_molecule_of_insoluble_aitken_mode_aerosol_in_air'][:]
        df['mass_SU_Ait'] = sample.variables['mass_fraction_of_sulfuric_acid_in_soluble_aitken_mode_dry_aerosol_in_air'][:] 
        df['mass_SU_acc'] = sample.variables['mass_fraction_of_sulfuric_acid_in_soluble_accumulation_mode_dry_aerosol_in_air'][:] 
        df['mass_SU_cor'] = sample.variables['mass_fraction_of_sulfuric_acid_in_soluble_coarse_mode_dry_aerosol_in_air'][:] 
        df['mass_BC_Ait'] = sample.variables['mass_fraction_of_black_carbon_in_soluble_aitken_mode_dry_aerosol_in_air'][:] 
        df['mass_BC_acc'] = sample.variables['mass_fraction_of_black_carbon_in_soluble_accumulation_mode_dry_aerosol_in_air'][:]
        df['mass_BC_cor'] = sample.variables['mass_fraction_of_black_carbon_in_soluble_coarse_mode_dry_aerosol_in_air'][:] 
        df['mass_BC_Aitins'] = sample.variables['mass_fraction_of_black_carbon_in_insoluble_aitken_mode_dry_aerosol_in_air'][:]
        df['mass_OC_Ait'] = sample.variables['mass_fraction_of_particulate_organic_matter_in_soluble_aitken_mode_dry_aerosol_in_air'][:]  
        df['mass_OC_acc'] = sample.variables['mass_fraction_of_particulate_organic_matter_in_soluble_accumulation_mode_dry_aerosol_in_air'][:]
        df['mass_OC_cor'] = sample.variables['mass_fraction_of_particulate_organic_matter_in_soluble_coarse_mode_dry_aerosol_in_air'][:]
        df['mass_OC_Aitins'] = sample.variables['mass_fraction_of_particulate_organic_matter_in_insoluble_aitken_mode_dry_aerosol_in_air'][:] 
        df['mass_SS_acc'] = sample.variables['mass_fraction_of_seasalt_in_soluble_accumulation_mode_dry_aerosol_in_air'][:]
        df['mass_SS_cor'] = sample.variables['mass_fraction_of_seasalt_in_soluble_coarse_mode_dry_aerosol_in_air'][:] 
        # a little gymnastic to get Datetime objs
        zero_time = datetime(1970,1,1,0,0)
        transformed_times = []
        for time in df['time']:
            target_time = zero_time + timedelta(hours=time)
            transformed_times.append(target_time)
        df['start'] = transformed_times
        df.drop(columns=['time'], inplace=True)

        parent_id = "SMOS_" + this.simulationSample.id
        df['parent'] = parent_id

        now_time = datetime.now()
        diff_time = (now_time - zero_time)
        versionTag= -1 * diff_time.total_seconds()
        df['dataVersion'] = versionTag

        output_records = df.to_dict(orient="records")

        # upsert this batch
        c3.SimulationModelOutput.upsertBatch(objs=output_records)

        this.processed = True
        c3.SimulationOutputFile.merge(this)
        return True
    else:
        return False
    


def upsertTestAOD(this):
    """
    Function to Open files in the SimulationOutputFile table with monthly-mean container and then populate TestAOD data.
    
    - Arguments:
        -this: an instance of SimulationOutputFile

    - Returns:
        -bool: True if file was processed, false if file has already been processed or if container type does not match.

    Return codes:
        0: All good!
        1: Failed to open NetCDFFile
        2: Failed to create DataFrame for variables
        3: Failed to create DataFrame for GeoSpaceTimePoint
        4: Failed to upsert GeoSpaceTimePoint
        5: Failed to upsert Simulation3HourlyAODData
        6: File does not have appropriate container for this method
    """
    import pandas as pd
    import numpy as np
    import datetime as dt

    # verify file container
    if(this.container == 'aod-3hourly'):
        variable_names = {
            "dust" : "atmosphere_optical_thickness_due_to_dust_ambient_aerosol",
            "solubleAitkenMode" : "atmosphere_optical_thickness_due_to_soluble_aitken_mode_ambient_aerosol",
            "solubleAccumulationMode" : "atmosphere_optical_thickness_due_to_soluble_accumulation_mode_ambient_aerosol",
            "solubleCoarseMode" : "atmosphere_optical_thickness_due_to_soluble_coarse_mode_ambient_aerosol",
            "insolubleAitkenMode" : "atmosphere_optical_thickness_due_to_insoluble_aitken_mode_ambient_aerosol"
        }
        #open file
        try:
            sample = c3.NetCDFUtil.openFile(this.file.url)
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.datetime.now(),
                    lastAttemptFailed=True,
                    returnCode=1)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            return False


        try:
            df_var = pd.DataFrame()
            # this is to take care of variables that need to be flattened
            for var in variable_names.items():
                tensor = sample[var[1]][:][2,:,:,:]
                tensor = np.array(tensor).flatten()
                df_var[var[0]] = tensor
            # include simulation sample
            df_var["simulationSample"] = this.simulationSample
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.datetime.now(),
                    lastAttemptFailed=True,
                    returnCode=2)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            c3.NetCDFUtil.closeFile(sample, this.file.url)
            return False

        try:
            # now do spacetime coordinates
            df_st = pd.DataFrame()

            lat = sample["latitude"][:]
            lon = [x*(x < 180) + (x - 360)*(x >= 180) for x in sample["longitude"][:]]
            tim = sample["time"][:]
            zero_time = dt.datetime(1970,1,1,0,0)
            times = []
            for t in tim:
                target_time = zero_time + dt.timedelta(hours=t)
                times.append(target_time)
            

            df_st["time"] = [t for t in times for n in range(0, len(lat)*len(lon))]
            df_st["latitude"] = [l for l in lat for n in range(0, len(lon))]*len(times)
            df_st["longitude"] = [l for l in lon]*len(times)*len(lat)

            df_st["id"] = round(df_st["latitude"],3).astype(str) + "_" + round(df_st["longitude"],3).astype(str) + "_" + df_st["time"].astype(str).apply(lambda x: x.replace(" ", 'T'))
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.datetime.now(),
                    lastAttemptFailed=True,
                    returnCode=3)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            c3.NetCDFUtil.closeFile(sample, this.file.url)
            return False

        try:
        # now upsert this
            output_records = df_st.to_dict(orient="records")
            gst = c3.TestGSTP.upsertBatch(objs=output_records)
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.datetime.now(),
                    lastAttemptFailed=True,
                    returnCode=4)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            c3.NetCDFUtil.closeFile(sample, this.file.url)
            return False

        try:
            df_batch = pd.DataFrame(df_var)
            df_batch["geoSurfaceTimePoint"] = gst.objs
            output_records = df_batch.to_dict(orient="records")
            c3.TestAOD.createBatch(objs=output_records)
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.datetime.now(),
                    lastAttemptFailed=True,
                    returnCode=5)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            c3.NetCDFUtil.closeFile(sample, this.file.url)
            return False

        # if we get here, it worked
        meta = c3.MetaFileProcessing(lastProcessAttempt=dt.datetime.now(),
                    lastAttemptFailed=False,
                    returnCode=0)
        c3.SimulationOutputFile(id=this.id, processed=True, processMeta=meta).merge()
        c3.NetCDFUtil.closeFile(sample, this.file.url)
        return True
    
    else:
        meta = c3.MetaFileProcessing(lastProcessAttempt=dt.datetime.now(),
                    lastAttemptFailed=True,
                    returnCode=6)
        c3.SimulationOutputFile(id=this.id, processed=True, processMeta=meta).merge
        return False


def upsertData(this):
    """
    Function to Open files in the SimulationOutputFile table then populates Simulation***Output data.
    
    - Arguments:
        -this: an instance of SimulationOutputFile

    - Returns:
        -bool: True if file was processed, false if file has already been processed 
    """
    if(this.container == 'aod-3hourly'):
        return this.upsert3HourlyAODData()
    elif(this.container == 'acure-aircraft'):
        return this.upsertAcureAircraftData()
    else:
        return False


def upsert3HourlyAODData(this):
    """
    Function to Open files in the SimulationOutputFile table with monthly-mean container and then populate Simulation3HourlyAODOutput data.
    
    - Arguments:
        -this: an instance of SimulationOutputFile

    - Returns:
        -bool: True if file was processed, false if file has already been processed or if container type does not match.

    Return codes:
        0: All good!
        1: Failed to open NetCDFFile
        2: Failed to create DataFrame for variables
        3: Failed to create DataFrame for GeoSpaceTimePoint
        4: Failed to upsert GeoSpaceTimePoint
        5: Failed to upsert Simulation3HourlyAODData
        6: File does not have appropriate container for this method
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime as dt

    # verify file container
    if(this.container == 'aod-3hourly'):
        variable_names = {
            "dust" : "atmosphere_optical_thickness_due_to_dust_ambient_aerosol",
            "solubleAitkenMode" : "atmosphere_optical_thickness_due_to_soluble_aitken_mode_ambient_aerosol",
            "solubleAccumulationMode" : "atmosphere_optical_thickness_due_to_soluble_accumulation_mode_ambient_aerosol",
            "solubleCoarseMode" : "atmosphere_optical_thickness_due_to_soluble_coarse_mode_ambient_aerosol",
            "insolubleAitkenMode" : "atmosphere_optical_thickness_due_to_insoluble_aitken_mode_ambient_aerosol"
        }
        #open file
        try:
            sample = c3.NetCDFUtil.openFile(this.file.url)
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.now(),
                    lastAttemptFailed=True,
                    returnCode=1)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            return False


        try:
            df_var = pd.DataFrame()
            # this is to take care of variables that need to be flattened
            for var in variable_names.items():
                tensor = sample[var[1]][:][2,:,:,:]
                tensor = np.array(tensor).flatten()
                df_var[var[0]] = tensor
            # include simulation sample
            df_var["simulationSample"] = this.simulationSample
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.now(),
                    lastAttemptFailed=True,
                    returnCode=2)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            c3.NetCDFUtil.closeFile(sample, this.file.url)
            return False

        try:
            # now do spacetime coordinates
            df_st = pd.DataFrame()

            lat = sample["latitude"][:]
            lon = [x*(x < 180) + (x - 360)*(x >= 180) for x in sample["longitude"][:]]
            ts = this.dateTag
            times = [ts.replace(hour=3), ts.replace(hour=6), ts.replace(hour=9), 
                ts.replace(hour=12), ts.replace(hour=15), ts.replace(hour=18), 
                ts.replace(hour=21), ts.replace(hour=0)]

            df_st["time"] = [t for t in times for n in range(0, len(lat)*len(lon))]
            df_st["latitude"] = [l for l in lat for n in range(0, len(lon))]*len(times)
            df_st["longitude"] = [l for l in lon]*len(times)*len(lat)

            df_st["id"] = round(df_st["latitude"],3).astype(str) + "_" + round(df_st["longitude"],3).astype(str) + "_" + df_st["time"].astype(str).apply(lambda x: x.replace(" ", 'T'))
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.now(),
                    lastAttemptFailed=True,
                    returnCode=3)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            c3.NetCDFUtil.closeFile(sample, this.file.url)
            return False

        try:
        # now upsert this
            output_records = df_st.to_dict(orient="records")
            gst = c3.GeoSurfaceTimePoint.upsertBatch(objs=output_records)
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.now(),
                    lastAttemptFailed=True,
                    returnCode=4)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            c3.NetCDFUtil.closeFile(sample, this.file.url)
            return False

        try:
            df_batch = pd.DataFrame(df_var)
            df_batch["geoSurfaceTimePoint"] = gst.objs
            output_records = df_batch.to_dict(orient="records")
            c3.Simulation3HourlyAODOutput.createBatch(objs=output_records)
        except:
            meta = c3.MetaFileProcessing(lastProcessAttempt=dt.now(),
                    lastAttemptFailed=True,
                    returnCode=5)
            c3.SimulationOutputFile(id=this.id, processMeta=meta).merge()
            c3.NetCDFUtil.closeFile(sample, this.file.url)
            return False

        # if we get here, it worked
        meta = c3.MetaFileProcessing(lastProcessAttempt=dt.now(),
                    lastAttemptFailed=False,
                    returnCode=0)
        c3.SimulationOutputFile(id=this.id, processed=True, processMeta=meta).merge()
        c3.NetCDFUtil.closeFile(sample, this.file.url)
        return True
    
    else:
        meta = c3.MetaFileProcessing(lastProcessAttempt=dt.now(),
                    lastAttemptFailed=True,
                    returnCode=6)
        c3.SimulationOutputFile(id=this.id, processed=True, processMeta=meta).merge
        return False