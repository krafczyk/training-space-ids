function beforeRemove(objs) {
    objs.forEach(function(hf) {
       if (hf.file){
         hf.file.delete()
       }
    });
    return c3Make("ObjList<HindcastFile>",{objs: objs})
    ;
};