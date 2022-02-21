
function beforeRemove(objs) {
    var typeName = objs[0].toJson()['type']
    objs.forEach(function(f) {
       if (f.raw_image_file.exists()){
          f.raw_image_file.delete();
       }
       if (f.processed_image_file.exists()){
          f.processed_image_file.delete();
       }
    });
    return c3Make("ObjList<"+typeName+">",{objs: objs});
};