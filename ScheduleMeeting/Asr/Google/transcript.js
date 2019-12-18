const speech  = require('@google-cloud/speech').v1p1beta1;
const {Storage} = require('@google-cloud/storage');
const fs      = require('fs');




async function uploadFileToGCS(audioFilePath, audioFileName) {
         const storage = new Storage();
         const bucketName = 'gs://voice2note';
        var resp =  await storage.bucket(bucketName).upload(audioFilePath, {
                 gzip: false,
                 metadata: {
                         cacheControl: 'public, max-age=31536000',
                 }
         });
 //	console.log(resp);
 	return Promise.resolve(bucketName+"/"+audioFileName)

}

async function getTranScript(recordingUrl, audioFilePath, uniqId) {
  const client      = new speech.SpeechClient();
 // const file        = fs.readFileSync(audioFilePath);
 // const audioBytes  = file.toString('base64');
 // var transcription = "";
  var conversation = []
  var prevTag;
  var text;

 /* const audio = {
    content: audioBytes,
  };*/

  const audio = {
 	 uri: audioFilePath
	}

  const config = {
    encoding: 'WAV',
    sampleRateHertz: 8000,
    languageCode: 'en-US',
    enableAutomaticPunctuation: true,
    enableSpeakerDiarization: true,
    diarizationSpeakerCount:4,
    useEnhanced: true,
    model: 'phone_call'
  };

  const request = {
    audio: audio,
    config: config,
  };
console.log(request,">>>>>>>>>>>><<<<<<<<<<<<<<<");
/* const [response] = await client.recognize(request);
  response.results.map(function(result){
    transcription = transcription+result.alternatives[0].transcript
  }).join('\n');
  console.log("Transcription: "+transcription);
  return Promise.resolve({"Google":transcription}); */
// const [response] = await client.recognize(request);

  const [operation] = await client.longRunningRecognize(request);
  const [response] = await operation.promise();
  console.log(response);
  const transcription = response.results
  .map(result => result.alternatives[0].transcript)
  .join('\n');
  const result = response.results[response.results.length - 1];
  const wordsInfo = result.alternatives[0].words;
	
var words = wordsInfo;
//console.log(words, "Diarization............>>>>>>>>>>>");
  for(i=0; i<words.length; i++){
      var currentTag = words[i].speakerTag;
      if(prevTag){
		if(currentTag == prevTag){
			text = text+" "+words[i].word;
		}else{
			var obj = {};
			var key = "speaker"+prevTag.toString();
			var string = key+": "+text;
			conversation.push(string);
			text = words[i].word;
			prevTag = currentTag;
		}	
	}else{
		prevTag = currentTag;
		text = words[i].word;
	}

	if(i == words.length-1){
		var obj = {};
		var key = "speaker"+prevTag.toString();
		var string = key+": "+text
		conversation.push(string);
	}
}
return Promise.resolve({"transcription":{"Google":transcription}, "conversation":{"Google":conversation}});
}
module.exports = {
  "getTranScript" : getTranScript,
  "uploadFileToGCS": uploadFileToGCS
}
