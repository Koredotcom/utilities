const process   = require("../process.js");
const Promise   = require("bluebird");
const fs        = require("fs");
const {getDataFromMongo, setDataToMongo} = require("../methods/mongoActions.js");
const {pre_meeting_info, post_meeting_info} = require("../models/meeting_info.js");
const {sendMail} 	= require("../methods/mail.js");


async function speechTotext(recordingUrl, audiFilePath, uniqId){
  var allASRs   = Object.keys(process.ASR);
  var promises  = allASRs.map(function(asr){
    let asrObj  = Object.assign({}, process.ASR[asr]);
    if(asrObj.available){
      var {getTranScript} = require("./"+asr+"/transcript.js");
      return getTranScript(recordingUrl,audiFilePath,uniqId);
    }
  });
  
  return Promise.all(promises)
  .then(async function(allTranscripts){
    console.log(allTranscripts)
    var transcriptions = [];
    var conversations = [];
    allTranscripts.forEach(function(transcript){
      if(transcript){
        transcriptions.push(transcript.transcription);
	conversations.push(transcript.conversation);
      }
    });
    var doc = await getDataFromMongo(pre_meeting_info, {"uniqId":uniqId});
    if(doc.length){
      var obj = {};
      obj['from']           = doc[0].from;
      obj['to']             = doc[0].to;
      obj['startDateTime']  = doc[0].startDateTime;
      obj['endDateTime']    = doc[0].endDateTime;
      obj['uniqId']         = uniqId;
      obj['transcript']     = JSON.stringify(transcriptions);
      obj['recordingUrl']   = recordingUrl;
      obj['conversation']   = JSON.stringify(conversations);
      obj['messageId']      = doc[0].messageId;
      sendMail(obj);	
      return setDataToMongo(post_meeting_info, obj);
    }
  });
}

module.exports = {
  "speechTotext" : speechTotext
}
