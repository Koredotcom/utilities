const {pre_meeting_info, post_meeting_info} = require("../models/meeting_info.js");
const {getDataFromMongo}  =   require("./mongoActions.js");

const getPreMeetingInfo = async function(req,res){
	return getDataFromMongo(pre_meeting_info)
	.then(function(data){
		res.send(data);
	});
}	

const getPostMeetingInfo = async function(req,res){
	return getDataFromMongo(post_meeting_info)
	.then(function(data){
		res.send(data);
	});
}


module.exports = {
	"getPreMeetingInfo" : getPreMeetingInfo,
	"getPostMeetingInfo" : getPostMeetingInfo
} 