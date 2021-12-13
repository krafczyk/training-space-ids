function beforeRemove(objs) {
    objs.forEach(function(f) {
       if (f.file){
         f.file.delete()
       }
    });
    return c3Make("ObjList<FMRCFile>",{objs: objs})
    ;
};