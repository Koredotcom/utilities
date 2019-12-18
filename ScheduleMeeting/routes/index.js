const express 				= require('express');
const {getAuthCode} 		= require("../methods/authCode.js");
const {notification}		= require("../methods/notification.js");
const {getPreMeetingInfo, getPostMeetingInfo} 
							= require("../methods/meetingInfo.js");
const {twilioRecord}		= require("../Twilio/recording.js");
const process				= require("../process.js");


const router = new express.Router();

router.get(process.apiPrefix  +'/authcode/get', getAuthCode);
router.post(process.apiPrefix +'/outlook/notification', notification);
router.get(process.apiPrefix  +'/pre_meeting/info/get',getPreMeetingInfo);
router.get(process.apiPrefix  +'/post_meeting/info/get',getPostMeetingInfo);
router.post(process.apiPrefix +'/twilio/record',twilioRecord);


module.exports = router;
