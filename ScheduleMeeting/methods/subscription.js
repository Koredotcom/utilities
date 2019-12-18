const request     = require("request");
const template    = require("url-template");
const process     = require("../process");
const redisActions = require('./redisActions.js');

const pub         = require("../RedisClient.js").createClient();
const sub         = require("../RedisClient.js").createClient();

pub.config("SET", "notify-keyspace-events", "KExA");

function setTokenInRedis(key, value, ttl) {
    pub.set(key,value);
    if(ttl){
      pub.set(key,value);
      pub.expire(key,ttl);
      sub.subscribe("__keyspace@0__:" +key);
    }
}

sub.on('message', function (channel, msg) {
    if (msg == "expired") {
      console.log(channel)
      let id = channel.split(":")[1];
      if(id == "SUBSCRIPTION_ID")
        return reSubscription("RESUBSCRIPTION_ID");
    }
});

async function subscribeToOutlook(accessToken){
  var RESOURCE_URL = template.parse(process.RESOURCE_URL).expand({SHARED_EMAIL_ID: process.SHARED_EMAIL_ID});
  var options = { 
    method: 'POST',
    url: process.SUBSCRIPTION_URL,
    headers:{
      authorization: 'Bearer '+accessToken,
     'content-type': 'application/json' 
    },
    body:{
      '@odata.type'     : '#Microsoft.OutlookServices.PushSubscription',
      'Resource'        : RESOURCE_URL,
      'NotificationURL' : process.NOTIFICATION_URL,
      'ChangeType'      : 'Created',
      'ClientState'     : '1234567' 
    },
    json: true 
  };
  request(options, async function (error, response, body) {
    console.log(response.statusCode,"statusCode")
    if (error){
      console.log("Subcription request failed")
      return Promise.reject(error);
    }
    if(response.statusCode == 201 || response.statusCode == 200){
      console.log("******************************")
      await setTokenInRedis("SUBSCRIPTION_ID",body.Id,604500) //TTL: 7 days(-5mintues)
      await setTokenInRedis("RESUBSCRIPTION_ID",body.Id)
    }
    console.log("SUBSCRIPTION>>>>>>>>>>>>>>>>>",body);
  });
}

async function reSubscription(key){
  var accessToken = await redisActions.getDataFromRedis("OUTLOOK_ACCESS_TOKEN_KORA");
  var subscriptionID = await redisActions.getDataFromRedis(key);
  var options = {
    method: 'PATCH',
    url: process.SUBSCRIPTION_URL+'/'+subscriptionID,
    headers:{
      'content-type': 'application/json',
      "authorization": 'Bearer '+accessToken
    },
    body: { 
        '@odata.type': '#Microsoft.OutlookServices.PushSubscription'
      },
    json: true
  };

  request(options, async function (error, response, body) {
    console.log(body);
    if (error) {
      console.log("Erro during re-subscription")
      return Promise.reject(error);
    } else if (response.statusCode === 201 || response.statusCode === 200) {
      await setTokenInRedis("SUBSCRIPTION_ID",body.Id,604500) //TTL: 7 days(-5mintues)
      await setTokenInRedis("RESUBSCRIPTION_ID",body.Id) 
    } else {
      const errorMessage = JSON.stringify(body);
      console.log('statusCode - ' + response.statusCode + ' - Error during re-subscription >> ' + errorMessage);
    }
  });
}

module.exports = {
  "subscribeToOutlook" : subscribeToOutlook
}