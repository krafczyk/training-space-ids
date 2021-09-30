def upsertFiles(this):
    """
    Upserts the NetCDF files from a SimulationSample instance to the SimulationOutputFile persisted table.

    Arguments:
    -----
    Returns:
        -int: Number of files upserted
    """
    from datetime import datetime

    ensemble_path = c3.FileSystem.inst().rootUrl() + 'gordon-group' + this.ensemble.name + '/'
    prepath_to_all_files = ensemble_path + this.ensemble.prePathToFiles 
    path_to_sample = prepath_to_all_files + str(this.simulationNumber).zfill(3) + '/'
    file_list = c3.FileSystem.inst().listFiles(path_to_sample).files

    SimOutFileObjs = []
    for file in file_list:
        if file.url[-3:] == '.nc':
            file_obj = c3.File.makeObj({
                "url": file.url
            })
            date_str = file.url[-11:-3]
            date_dt = datetime.strptime(date_str, '%Y%m%d')
            SimOutFileObjs.append(c3.SimulationOutputFile(**{
                "simulationSample": this,
                "file": file_obj,
                "dateTag": date_dt
            }))

    c3.SimulationOutputFile.upsertBatch(SimOutFileObjs)
    return len(SimOutFileObjs)