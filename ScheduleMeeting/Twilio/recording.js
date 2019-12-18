const express   = require('express');
const fs        = require('fs');
const download  = require('download');
const VoiceResponse    = require('twilio').twiml.VoiceResponse;
const {uploadFileToGCS} = require("../Asr/Google/transcript.js");
const {speechTotext} = require("../Asr/speechtotext.js");
const path             = require("path");
const app = express();


async function downloadRecording(recordingUrl, uniqId){
  return download(recordingUrl+'.wav')
  .then(async function(data){
    var getId           = recordingUrl.split("/");
    var audioFileName   = getId[getId.length-1];
    var audioFilePath    = path.join(__dirname, '../Asr/audioFiles/'+audioFileName+'.wav');
    await fs.writeFileSync(audioFilePath, data);
    var updatedAudioFilePath =  await uploadFileToGCS(audioFilePath,audioFileName+'.wav');
    return speechTotext(recordingUrl, updatedAudioFilePath, uniqId);
  });
}


async function twilioRecord(req,res){
 
  if(req.body && req.body.RecordingUrl){
    return setTimeout(async function(){
	return downloadRecording(req.body.RecordingUrl, req.query.uniqId);
    },10000);
  }

  const twiml = new VoiceResponse(); 
  twiml.say('Hi, I am listening. Call time limit is one hour.');
  twiml.record({ transcribe: false, maxLength: 3600, recordingChannels: 'mono' });
  twiml.hangup();
  res.type('text/xml');
  res.send(twiml.toString());
}


module.exports = {
  "twilioRecord" : twilioRecord,
}

