const mongoose = require("mongoose");
const process = require("../process.js");

const pre_meeting_info = new mongoose.Schema({
	uniqId:{
		type:String
	},
	from:{
		type:String
	},
	to:{
		type:String
	},
	startDateTime:{
		type:String,
	},
	endDateTime:{
		type:String
	},
	phoneNumber:{
		type:String
	},
	passCode:{
		type:String
	},
	messageId:{
		type:String
	}
});

const post_meeting_info = new mongoose.Schema({
	uniqId:{
		type:String
	},
	from:{
		type:String
	},
	to:{
		type:String
	},
	startDateTime:{
		type:String,
	},
	endDateTime:{
		type:String
	},
	transcript:{
		type:String
	},
	phoneNumber:{
		type:String
	},
	passCode:{
		type:String
	},
	recordingUrl:{
		type:String
	},
	conversation:{
		type: String
	},
	messageId:{
		type:String
	}
});
module.exports.pre_meeting_info= mongoose.model(process.MONGO.PRE_MEETING_COLLECTION_NAME,	pre_meeting_info);
module.exports.post_meeting_info= mongoose.model(process.MONGO.POST_MEETING_COLLECTION_NAME,	post_meeting_info);

