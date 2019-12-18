const config      = require("../config");
const pub         = require("../RedisClient.js").createClient();


function setDataToRedis(key,value){
  return new Promise(function(resolve,reject){
    pub.set(key,value,function(err,res){
      if(err)
        return reject(err);
      return resolve(res);
    });
  });
}

function getDataFromRedis(key){
  return new Promise(function(resolve,reject){
    pub.get(key,function(err,res){
      if(err)
        return reject(err);
      return resolve(res);
    })
  });
}

function removeDataFromRedis(key){
  return new Promise(function(resolve,reject){
    pub.del(key,function(err,res){
      if(err)
        return reject(err);
      return resolve(res);
    })
  });
}

module.exports = {
  "setDataToRedis"    : setDataToRedis,
  "getDataFromRedis"    : getDataFromRedis,
  "removeDataFromRedis"   : removeDataFromRedis
}