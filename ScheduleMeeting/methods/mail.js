const request         = require("request");
const redisActions    = require('./redisActions.js');
const cheerio         = require('cheerio');
const {pre_meeting_info} = require("../models/meeting_info.js");
const {setDataToMongo}  =   require("./mongoActions.js");
const {getTimeDiffInSeconds} = require("./startmeeting.js");
const process           =  require("../process.js");

async function getMail(messageId){
	console.log(messageId, "Message ID >>>>>>>>>>>>>>>>>>>");
  var accessToken = await redisActions.getDataFromRedis("OUTLOOK_ACCESS_TOKEN_KORA");
  console.log(accessToken,"OUTLOOK_ACCESS_TOKEN_KORA")
  var options = {
    url: process.OUTLOOK_MESSAGES_URL+'/'+ messageId,
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + accessToken,
    },
  };
  request(options, function(err, response, body) {
    if (err) {
      console.log("Request to get mail failed")
      reject(err);
    }else{
      var respBody = JSON.parse(body);
      console.log(">>>>>>>>>>>>>>",respBody,">>>>>>>>>>>>>>>>>>>>")
      if(respBody && respBody.MeetingMessageType && respBody.MeetingMessageType == "MeetingRequest"){
        var obj = {
          "from": JSON.stringify(respBody.From),
          "to":JSON.stringify(respBody.ToRecipients),
	 "messageId":messageId
        }
        return parseMail(respBody.Body,obj);
      }
    }
  });
}

async function parseMail(message,obj){
  const $ = cheerio.load(message.Content);
  for(i=0; i<$('time').length;i++){
    var timeTag = $('time')[i];
    if(timeTag && timeTag.attribs && timeTag.attribs.itemprop){
      if(timeTag.attribs.itemprop == 'startDate'){
        obj["startDateTime"] = timeTag.attribs.datetime;
        console.log("--------------------------START DATE",timeTag.attribs.datetime,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");
      }
      if(timeTag.attribs.itemprop == 'endDate'){
        obj["endDateTime"] = timeTag.attribs.datetime;
        console.log("--------------------------END DATE",timeTag.attribs.datetime,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");
      }
    }
  };

  for(i=0;i<$('span').length;i++){
    var spanTag = $('span')[i];
    if(spanTag&&spanTag.attribs&&spanTag.attribs.itemprop&&(spanTag.attribs.itemprop == "phoneNumber" || spanTag.attribs.itemprop == "passCode")){
      console.log(i,spanTag.children[0].data)
      if(spanTag.children && spanTag.children.length && spanTag.children[0].data){
        var key = spanTag.attribs.itemprop == "phoneNumber"? "phoneNumber" : "passCode";
        obj[key] = spanTag.children[0].data;
      }
    }
  }

  obj['uniqId'] = new Date().getTime();

  if(obj["startDateTime"]){
    getTimeDiffInSeconds(obj["startDateTime"], obj);
  }

  return setDataToMongo(pre_meeting_info, obj);
}

async function sendMail (obj) {
  var messageId 	= obj["messageId"];
  var accessToken       = await redisActions.getDataFromRedis("OUTLOOK_ACCESS_TOKEN_KORA");
  var createReplyResp   = await createReply(messageId, accessToken);
  var updateMessageResp = await updateMessage(createReplyResp, accessToken, obj);

  let options = {
    url: 'https://outlook.office.com/api/v2.0/me/messages/'+updateMessageResp.body.Id+'/send',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + accessToken,
    },
    json: true
  };

  return new Promise(function (resolve, reject){
    request(options, function (error, response, body) {
      if (error) {
        return reject(error);
      }
      console.log(body)
      return resolve(response);
    });
  });

};

async function createReply (messageId, accessToken){
  let options = {
    url: 'https://outlook.office.com/api/v2.0/me/messages/'+messageId +'/createreplyall',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer '+ accessToken,
    },
    json: true
  };
  console.log(options)
  return new Promise(function (resolve, reject){
    request(options, function (error, response, body) {
      if (error) {
        return reject(error);
      }
      console.log(body)
      return resolve(response);
    });
  }); 
}


async function updateMessage (response, accessToken, obj){
	if(obj && obj['transcript']){
		var objParse = JSON.parse(obj["transcript"]);
		var transcript = objParse[0].Google;
	}else{
		var transcript = "No transcript available";
	}
	if(obj && obj["conversation"]){
		var objParse = JSON.parse(obj["conversation"]);
		var conversationArr = objParse[0].Google;
		var text = "";
		conversationArr.forEach(function(convo){
			text = text+"<br>"+convo;
		});
	}
  let options = {
    url: 'https://outlook.office.com/api/v2.0/me/messages/'+response.body.Id, 
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + accessToken,
    },
    body: {
      'Body': {
        'ContentType': 'html',
        'Content':"Hi All, <br><br> <u>MOM:</u> <br> <u>Transcript:</u> "+transcript+"<br><u>Diarization:</u><br>"+text,
      }
    },
    json: true
  };
  return new Promise(function (resolve, reject){
    request(options, function (error, response, body) {
      if (error) {
        return reject(error);
      }
      console.log(body)
      return resolve(response);
    });
  });
}

module.exports = {
  "getMail" : getMail,
  "sendMail" : sendMail
}


