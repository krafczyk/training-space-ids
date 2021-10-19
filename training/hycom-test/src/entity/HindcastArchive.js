/**
 * 
 */
function afterCreate(objs) {
    objs.foreach(function(archv) {
       archv.stageFiles() 
    });
};

function afterUpdate(objs) {
    objs.foreach(function(archv) {
       archv.stageFiles() 
    });
};