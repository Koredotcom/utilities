const process = require("../process.js");

function makeACall(uniqId, toPhoneNumber, PIN){
	if(!toPhoneNumber) return;
	const client = require('twilio')(process.TWILIO.ACCOUNT_ID, process.TWILIO.AUTH_TOKEN);
	var options = {
		url: process.TWILIO.CALLBACK_URL+"?uniqId="+uniqId,
	        to: toPhoneNumber,
       		from: process.TWILIO.FROM_PHONE_NUMBER
   	 };

    if(PIN){
    	options['sendDigits'] = PIN;
    }
	client.calls.create(options)
    .then(function(call){
    	console.log('Call placed :', call.sid)
    });
}

module.exports = {
	"makeACall" : makeACall
}


