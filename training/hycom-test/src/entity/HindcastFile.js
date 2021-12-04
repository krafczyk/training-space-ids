function beforeRemove(objs) {
    objs.forEach(function(hf) {
       if (hf.file){
         hf.file.delete()
       }
    });
    return ObjList.make({"objs": objs});
};