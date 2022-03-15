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

function afterCreate(objs) {
  var files = objs.map(createFiles);
  files.forEach(upsertBatch);
  return;
  
  function upsertBatch(batch) {
    SimulationOutputFile.upsertBatch(batch);
  }
  
  function createFiles(obj) {
    var ensemble = SimulationEnsemble.fetch({
                      filter: Filter.eq("id",obj.ensemble.id) 
                    }).objs[0]

    // ACURE-AIRCRAFT CONTAINER                
    var ensemblePath = FileSystem.inst().rootUrl() + 'gordon-group/' + ensemble.name + '/';
    var prePathToAllFiles = ensemblePath + ensemble.prePathToFiles;
    var pathToSample = prePathToAllFiles + padStart(String(obj.simulationNumber),3,'0');
    var sampleFiles = FileSystem.inst().listFiles(pathToSample).files;
    // Remove non-NetCDF files from list
    for (var i = 0; i < sampleFiles.length; i++) {
      var sf = sampleFiles[i];
      if (sf.url.slice(-3) !== ".nc") {
        sampleFiles.splice(i,1);
      }
    }

    // MONTHLY-MEAN CONTAINER
    var pathToAllFiles = "azure://monthly-mean-simulations/";
    var sampleFiles2 = FileSystem.inst().listFiles(pathToAllFiles).files;
    // remove non netcdf stuff
    for (var i = 0; i < sampleFiles2.length; i++) {
      var sf = sampleFiles2[i];
      if (sf.url.slice(-3) !== ".nc") {
        sampleFiles2.splice(i,1);
      }
      else if (sf.url.slice(-6,-3) !== padStart(String(obj.simulationNumber), 3, '0')) {
        sampleFiles2.splice(i,1);
      }
    }

    // put two containers together
    sampleFiles = sampleFiles.concat(sampleFiles2);

    return sampleFiles.map(createSimOutFiles);
  
    function padStart(text, length, pad) {
      return (pad.repeat(Math.max(0, length - text.length)) + text).slice(-length);
    }
  
    function createSimOutFiles(file) {
      if (file.url.slice(0,32) === "azure://monthly-mean-simulations") {
        var year = file.url.slice(42,46);
        var month = file.url.slice(46,48);
        var day = file.slice(48,50);
        var date_str = year + "-" + month + "-" + day;
        var container = "monthly-mean";
        return SimulationOutputFile.make({
          "simulationSample": obj,
          "file": File.make({
                  "url": file.url
          }),
          "dateTag": DateTime.make({
                  "value": date_str
          }),
          "container": container
        });
      }
      else {
        var year = file.url.slice(-11,-7);
        var month = file.url.slice(-7,-5);
        var day = file.url.slice(-5,-3);
        var date_str = year + "-" + month + "-" + day;
        var container = "acure-aircraft";
        return SimulationOutputFile.make({
                  "simulationSample": obj,
                  "file": File.make({
                          "url": file.url
                  }),
                  "dateTag": DateTime.make({
                          "value": date_str
                  }),
                  "container": container
        });
      }
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

function upsertSampleData() {
  var results = this.outputFiles.map(upsert);

  function upsert(file) {
    var actual_file = SimulationOutputFile.get(file.id);
    return actual_file.upsertData();
  };

  var total = results.reduce(function (previousValue, currentValue) {
    return previousValue + currentValue;
  }, 0)

  return total;
};
