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
    // AZURE DIRECTORY PATH HERE: change 'gordon-group; to whatever you need
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
    return sampleFiles.map(createSimOutFiles);
  
    function padStart(text, length, pad) {
      return (pad.repeat(Math.max(0, length - text.length)) + text).slice(-length);
    }
  
    function createSimOutFiles(file) {
      var year = file.url.slice(-11,-7);
      var month = file.url.slice(-7,-5);
      var day = file.url.slice(-5,-3);
      var date_str = year + "-" + month + "-" + day;
      return SimulationOutputFile.make({
                  "simulationSample": obj,
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

function upsertSampleData(this) {
  this.outputFiles.forEach(upsertData);
}
