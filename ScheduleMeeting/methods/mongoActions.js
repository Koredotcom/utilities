let setDataToMongo = function(collection, obj){i
        return new Promise(function(resolve,reject){
                return new collection(obj)
                .save(function(err,res){
                if(err)
                        return reject("SET: MONGO ERROR "+err);
                return resolve("DONE");
        });
        });
}


let getDataFromMongo = function(collection, query){
        if(!query){
                query = {};
        }
        console.log(query)
        return new Promise(function(resolve,reject){
                return collection.find(query, function(err,docs){
                        if(err)
                                return reject('GET: MONGO ERROR '+err)
                        //console.log(docs, typeof docs);
                        docs = docs.reverse();
                        return resolve(docs);
                });
        });
}

let updateMongoData = function(collection){

}

module.exports = {
        "getDataFromMongo"      : getDataFromMongo,
        "setDataToMongo"        : setDataToMongo
}
