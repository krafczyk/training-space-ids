/**
 * 
 */
function afterCreate(objs) {
    objs.forEach(function(archv) {
       archv.stageFiles() 
    });
};

// function afterUpdate(objs) {
//     objs.forEach(function(archv) {
//        archv.stageFiles() 
//     });
// };