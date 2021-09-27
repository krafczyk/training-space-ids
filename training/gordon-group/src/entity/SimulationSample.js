/**
 * Callback that is called synchronously during a request that creates objs after those objs are created.  The
 * implementer can perform additional logic.
 *
 * @param objs
 *           List of objs that were created.  The objs will already have been created.  By default, only the id
 *           is present in the objs. If more fields are desired a dependency annotation can  be specified (e.g.
 *           `@dependency(include = "field1, field2...")`. Then the objs will have at least those requested fields.
 * @return List of any errors that were encountered.
 */
 //var objs = SimulationSample.fetch({'include':"this,ensemble.name"}).objs
function afterCreate(objs) {
    const extDir = 'gordon-group';
    let files = objs.map(createFiles);
    //let simOutFiles = files.map(getSimOutFiles)
    files.forEach(upsertBatch)
    return;
  
    function upsertBatch(batch) {
        SimulationOutputFile.upsertBatch(batch)
    }
  
    function createFiles(obj) {
      let d = obj.sampleKey
      d += String(obj.simId).padStart(3,'0');
      let d2=extDir + '/' + obj.ensemble.name +'/'+d
      //document.write(d2)
      let files = FileSystem.inst().listFiles(d2).files
      //document.write(files)
      return files.map(createSimOutFiles)
  
  
      function createSimOutFiles(file){
      return SimulationOutputFile.make(
      {
          "simulationSample": obj,
          "file": File.make(
          {
              "url": file.url
          }
          )
      }
      )
    }
    }
  }  