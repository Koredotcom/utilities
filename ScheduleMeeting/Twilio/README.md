//Options for "Dual" channel recording in Twilio
// Enabeling 'dual channel record'  in out goind call (dialin.js)

        var options = {
            record: 'record-from-answer-dual',
            url: process.TWILIO.CALLBACK_URL+"?uniqId="+uniqId,
            to: toPhoneNumber,
            from: process.TWILIO.FROM_PHONE_NUMBER
        };


//Enabling 'recodding dual channel' in record verb (recording.js)

 twiml.record({ transcribe: false, maxLength: 2400, recordingChannels: 'dual' });

