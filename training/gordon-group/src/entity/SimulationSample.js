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

// THIS IS NOT WORKING YET

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
      var ensemblePath = FileSystem.inst().rootUrl() + 'gordon-group/' + ensemble.name + '/';
      var prePathToAllFiles = ensemblePath + ensemble.prePathToFiles;
      var pathToSample = prePathToAllFiles + padStart(String(obj.simulationNumber),3,'0');

      var files = FileSystem.inst().listFiles(pathToSample).files;
      return files.map(createSimOutFiles);
  
      function padStart(text, length, pad) {
        return (pad.repeat(Math.max(0, length - text.length)) + text).slice(-length);
      }
  
      function createSimOutFiles(file){
        return SimulationOutputFile.make({
                  "simulationSample": obj,
                  "file": File.make({
                          "url": file.url
                          })
                  });
      }
    }
  }  