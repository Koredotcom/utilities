//To Enable multiChannel and multi Speaker tagging.
// Audio must have 2 Channel (Stereo)


//RequestConfig
  const config = {
    encoding: 'WAV',
    sampleRateHertz: 8000,
    languageCode: 'en-US',
    audioChannelCount: 2,
    enableAutomaticPunctuation: true,
    enableSeparateRecognitionPerChannel: true,
    enableSpeakerDiarization: true,
    diarizationSpeakerCount:4,
    useEnhanced: true,
    model: 'phone_call'
  };


  // Detects speech in the audio file
  const [response] = await client.recognize(request);
  const transcription = response.results
  .map(
    result =>
      ` Channel Tag: ${result.channelTag} ${result.alternatives[0].transcript}`
  )
  .join('\n');
console.log(`Transcription: \n${transcription}`);



//To Enable meeting time more than a minute 

Pre Req:
    Google Cloud Storage shoulbe created
	*) const bucketName = 'gs://voice2note';
   
    Have audio file 
	audio file =  bucketName + audioFile 
 
1) Upload audio file to gs
  const {Storage} = require('@google-cloud/storage');
  const util = require('util');


  const fs = require('fs');

  const storage = new Storage();
  const bucketName = 'gs://voice2note/';
  const fileName = 'RE2ab63447d9a66cf79a2f3faff27e6772_copy.wav';

  async function uploadFile() {
     // Uploads a local file to the bucket
     await storage.bucket(bucketName).upload(fileName, {
        // Support for HTTP requests made with `Accept-Encoding: gzip`
        gzip: false,
       // By setting the option `destination`, you can change the name of the
       // object you are uploading to a bucket.
     metadata: {
      // Enable long-lived HTTP caching headers
      // Use only if the contents of the file will never change
      // (If the contents will change, use cacheControl: 'no-cache')
      cacheControl: 'public, max-age=31536000',
    },
  });


  console.log(`${fileName} uploaded to ${bucketName}.`);

  uploadFile();


2) settimeout function to call the ASR after audio is uploaded to GS

3) Call ASR with GSURI

  const gcsUri = bucketName + fileName ;

  // Creates a client
  const client = new speech.SpeechClient();

  // The audio file's location, encoding, sample rate in hertz, and BCP-47 language code
  const audio = {
    uri: gcsUri
  };
 
  const config = {
    encoding: 'WAV',
    sampleRateHertz: 8000,
    languageCode: 'en-US',
    enableAutomaticPunctuation: true,
    enableSpeakerDiarization: true,
    diarizationSpeakerCount:2,
    useEnhanced: true,
    model: 'phone_call'
  };

  const request = {
    audio: audio,
    config: config,
  };

4) Response parsing is should call "client.longRunningRecognize"

const [operation] = await client.longRunningRecognize(request);
// Get a Promise representation of the final result of the job
const [response] = await operation.promise();
const transcription = response.results
  .map(result => result.alternatives[0].transcript)
  .join('\n');
console.log(`Transcription: ${transcription}`);

5) Diarization parsing is same as privious cases


