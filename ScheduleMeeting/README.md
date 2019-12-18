Meeting Note Generator
----------------------

Technology Stack:
-----------------

Source code is written in :  Node.js 
Email Scraping : Outlook REST API (moving to Kora's Haraka mail component) 
Scheduling : Redis 
Database : Mongo
For Voice Recording :  Twilio 
Audio to Text : Google ASR

Twilio Config:
-------------
Record : { transcribe: false, maxLength: 3600, recordingChannels: 'mono' };

Google ASR Config:
-----------------
Transcription Config : { encoding: 'WAV', sampleRateHertz: 8000, languageCode: 'en-US', enableAutomaticPunctuation: true, enableSpeakerDiarization: true, diarizationSpeakerCount:4, useEnhanced: true,
model: 'phone_call'
};

API for Kora’s Haraka mail component to consume:
------------------------------------------------

URL: http://xxx.yyy.net/schedulemeeting/v1/schedule/details Method: POST Authorization Token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx All Parameters: ["meeting_start_date_time","meeting_end_date_time","from_email","to_recipients", "cc_recipients", "bcc_recipients", "phone_number", "passcode","meeting_link","meeting_duration"] Mandatory Parameters: meeting_start_date_time, passcode & phone_number

Sample CURL request:

curl -X POST
http://xxx.yyy.net/schedulemeeting/v1/schedule/details
-H 'authorization: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
-H 'cache-control: no-cache'
-H 'content-type: application/json'
-H 'postman-token: 11111111111111111111111111111111'
-d '{ "meeting_start_date_time":"20191218070519", "passcode":"1234", "phone_number":"12243545" }'
