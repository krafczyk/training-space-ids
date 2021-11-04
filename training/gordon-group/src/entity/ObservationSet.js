/**
 * Callback that is called synchronously during a request 
 * that creates objs after those objs are created. 
 *
 * @param objs
 *  List of objs that were created.  
 *  The objs will already have been created.  
 *  By default, only the id is present in the objs. 
 *  If more fields are desired a dependency annotation can  be specified 
 * (e.g. `@dependency(include = "field1, field2...")`. 
 * Then the objs will have at least those requested fields.
 * @return List of any errors that were encountered.
 */

 function afterCreateObs(objs) {
    var files = objs.map(createObsFiles);
    files.forEach(upsertBatch);
    return;
    
    function upsertBatch(batch) {
      ObservationOutputFile.upsertBatch(batch);
    }
    
    function createObsFiles(obj) {
      // AZURE DIRECTORY PATH HERE: change 'gordon-group; to whatever you need
      var observationPath = FileSystem.inst().rootUrl() + 'gordon-group/' + observationSet.name + '/';
      var prePathToAllFiles = observationPath + observationSet.prePathToFiles;
  
      var observationFiles = FileSystem.inst().listFiles(prePathToAllFiles).files;
      // Remove non-NetCDF files from list
      for (var i = 0; i < observationFiles.length; i++) {
        var sf = observationFiles[i];
        if (sf.url.slice(-3) !== ".nc") {
          observationFiles.splice(i,1);
        }
      }
      return observationFiles.map(createObsOutFiles);
    
      function padStart(text, length, pad) {
        return (pad.repeat(Math.max(0, length - text.length)) + text).slice(-length);
      }
    
      function createObsOutFiles(file) {
        var year = file.url.slice(-11,-7);
        var month = file.url.slice(-7,-5);
        var day = file.url.slice(-5,-3);
        var date_str = year + "-" + month + "-" + day;
        return ObservationOutputFile.make({
                    "observation": obj,
                    "file": File.make({
                            "url": file.url
                    }),
                    "dateTag": DateTime.make({
                            "value": date_str
                    })
        });
      }
    }
  };
  
  
  
  
  
  /**
   * Function to upsert SimulationModelOutput with data from all SimulationOutputFiles
   * corresponding to this Simulation Sample
   * @param this, outputFiles
   *  List of SimulationOutputFiles corresponding to this SimulationSample. 
   *
   * @return Number of files that were processed
   */
  
  function upsertObservationData() {
    var results = this.outputFiles.map(upsert);
  
    function upsert(file) {
      var actual_file = ObservationOutputFile.get(file.id);
      return actual_file.upsertORACLESData();
    };
  
    var total = results.reduce(function (previousValue, currentValue) {
      return previousValue + currentValue;
    }, 0)
  
    return total;
  };
  