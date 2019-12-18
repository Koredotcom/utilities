const request       = require("request");
const template	    =	require("url-template");
const process       = require("../process.js");
const redisActions   = require('./redisActions.js');
const {subscribeToOutlook} = require("./subscription.js");


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
    console.log("REDIS EXPIRY EVENT >>>>>>>>>>>>>>>>>>>>>>", channel, msg);
    if (msg == "expired") {
      let id = channel.split(":")[1];
      console.log("KEY NAME >>>>>>>>>>>>>>>>.", id);
      if(id == "OUTLOOK_ACCESS_TOKEN_KORA"){
	console.log("GET REFRESHED TOKEN >>>>>>>");
        return getRefreshedToken("OUTLOOK_REFRESH_TOKEN");
      }
    }
});

function options(){
  var options = { 
    method: 'POST',
    url: template.parse(process.OAUTH_TOKEN_URL).expand({TENANT_ID: process.APP.TENANT_ID}),
    headers:{
      'content-type': 'application/x-www-form-urlencoded'
    },
    form:{
      client_id     : process.APP.CLIENT_ID,
      redirect_uri  : process.REDIRECT_URL,
      client_secret : process.APP.CLIENT_SECRET
    }
  };
  return options;
}

function getAuthToken(req,res,authCode,state){
    var _options = new options(),
        key_access_token = 'OUTLOOK_ACCESS_TOKEN_KORA',
        key_refresh_token = 'OUTLOOK_REFRESH_TOKEN'; 

    _options['form']['grant_type'] = 'authorization_code';
    _options['url'] = template.parse(process.OAUTH_TOKEN_URL).expand({TENANT_ID: process.APP.TENANT_ID});
    _options['form']['code'] = authCode;

    if(!state ||  state != "outlook") return;

    request(_options, async function (err, response, body) {
    if (response.statusCode === 200) {
      var respBody      = JSON.parse(body);
      var accessToken   = respBody.access_token,
          refreshToken  = respBody.refresh_token,
          expiresIn     = respBody.expires_in;
      await setTokenInRedis(key_access_token, accessToken, expiresIn-300); //TTL: 55min
      await setTokenInRedis(key_refresh_token, refreshToken);
      var isSubscribed = await redisActions.getDataFromRedis("SUBSCRIPTION_ID")
      console.log(isSubscribed,">>>>>>>>>>>>>>>>>>>>>>")
      if(! isSubscribed){
        console.log("NO existing data...........>>>>")
        await subscribeToOutlook(accessToken);
      }else{
      console.log("TOKEN EXIST SO NO SUBSCRIPTION_ID",);
    }
      res.send({
        message: 'Request to get ' + req.query.state + ' accesstoken done.',
      });
    } else {
      res.status(400);
      res.send({
        message: 'Request to get ' + req.query.state + ' accesstoken failed.',
        errorMessage: response.body,
      });
    }
    console.log(body,"getAuthToken") 
  });
}

async function getRefreshedToken(key){
  return redisActions.getDataFromRedis(key)
  .then(function(refreshToken){
    var _options = options(),
        key_access_token = 'OUTLOOK_ACCESS_TOKEN_KORA',
        key_refresh_token = 'OUTLOOK_REFRESH_TOKEN';

    _options['form']['grant_type'] = 'refresh_token';
    _options['url'] = process.REFRESH_TOKEN_URL;
    _options['form']['refresh_token'] = refreshToken;
    console.log(_options);
    request(_options, async function (err, response, body) {
      if (err) {
        console.log({"message": 'Request to get accesstoken failed.',"err":err});
        return Promise.reject(err);
      } else if (response.statusCode === 200) {
        var respBody      = JSON.parse(body);
        var accessToken   = respBody.access_token,
            refreshToken  = respBody.refresh_token,
            expiresIn     = respBody.expires_in;
        await setTokenInRedis(key_access_token, accessToken,expiresIn-300); //TTL: 55min
        await setTokenInRedis(key_refresh_token, refreshToken);
        console.log({'message': 'Request to get accesstoken done.'});
      } else {
        console.log({"message": 'Request to get accesstoken failed.'});
      } 
      console.log(body,"getRefreshedToken");
    });
  });
}


module.exports = {
	"getAuthToken" : getAuthToken
}
