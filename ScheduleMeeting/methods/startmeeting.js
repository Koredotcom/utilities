const pub         = require("../RedisClient.js").createClient();
const sub         = require("../RedisClient.js").createClient();
const {makeACall} = require("../Twilio/dialin.js");

pub.config("SET", "notify-keyspace-events", "KExA");

function setMeetingTimeInRedis(key, value, ttl) {
    pub.set(key,value);
    if(ttl){
      pub.set(key,value);
      pub.expire(key,ttl);
      sub.subscribe("__keyspace@0__:" +key);
    }
}

sub.on('message', function (channel, msg) {
	console.log("**************")
    if (msg == "expired") {
      let id = channel.split(":")[1];
      console.log(id)
      pub.get(id+":meetingInfo",function(err,res){
      	console.log(res, "START MEETING.............");
      	var res = JSON.parse(res);
      	if(res){
      		if(res.phoneNumber){
      			var phoneNumber = res.phoneNumber;
      		}
      		if(res.passCode){
      			var passCode = res.passCode;
      		}
      		if(res.uniqId){
      			var uniqId = res.uniqId
      		}
      	}
      	return makeACall(uniqId, phoneNumber, passCode);
      });
    }
});

async function getTimeDiffInSeconds(startDateTime, obj){
	var splitDateTime 	= startDateTime.split("T");
	var getDate         = splitDateTime[0].match(/.{1,2}/g);
	var getTime			= splitDateTime[1].match(/.{1,2}/g);
	var date 			= getDate[0]+getDate[1]+"-"+getDate[2]+"-"+getDate[3];
	var time 			= getTime[0]+":"+getTime[1]+":"+getTime[2]+".000Z";
	var dateTime 		= date+"T"+time;

	var timeInSeconds = parseInt((new Date(dateTime).getTime() - new Date().getTime())/1000);
	console.log(timeInSeconds,"timeInSeconds")

	if(timeInSeconds > 0){
		var key = new Date().getTime();
		await setMeetingTimeInRedis(key+":meeting", JSON.stringify(obj), timeInSeconds);
		await setMeetingTimeInRedis(key+":meetingInfo", JSON.stringify(obj));
	}
}

module.exports = {
	"getTimeDiffInSeconds" : getTimeDiffInSeconds
}