const cheerio = require('cheerio')

var body = {
  contentType: 'html',
  content: '<html>\r\n' +
    '<head>\r\n' +
    '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\r\n' +
    '<meta content="text/html; charset=utf-8">\r\n' +
    '</head>\r\n' +
    '<body>\r\n' +
    '<span itemscope="" itemtype="http://schema.org/InformAction"><span itemprop="about" itemscope="" itemtype="http://schema.org/Person" style="display:none">\r\n' +
    '<meta itemprop="description" content="Invitation from ramesh.silveru@kore.com">\r\n' +
    '</span><span itemprop="object" itemscope="" itemtype="http://schema.org/Event">\r\n' +
    '<div style="">\r\n' +
    '<table cellspacing="0" cellpadding="8" border="0" summary="" style="width:100%; font-family:Arial,Sans-serif; border:1px Solid #ccc; border-width:1px 2px 2px 1px; background-color:#fff">\r\n' +
    '<tbody>\r\n' +
    '<tr>\r\n' +
    '<td>\r\n' +
    '<meta itemprop="eventStatus" content="http://schema.org/EventScheduled">\r\n' +
    '<h4 style="padding:6px 0; margin:0 0 4px 0; font-family:Arial,Sans-serif; font-size:13px; line-height:1.4; border:1px Solid #fff; background:#fff; color:#090; font-weight:normal">\r\n' +
    '<strong>You have been invited to the following event.</strong></h4>\r\n' +
    '<div style="padding:2px"><span itemprop="publisher" itemscope="" itemtype="http://schema.org/Organization">\r\n' +
    '<meta itemprop="name" content="Google Calendar">\r\n' +
    '</span>\r\n' +
    '<meta itemprop="eventId/googleCalendar" content="2b1fh0u82nbinih9t6b2qum9gb">\r\n' +
    '<h3 style="padding:0 0 6px 0; margin:0; font-family:Arial,Sans-serif; font-size:16px; font-weight:bold; color:#222">\r\n' +
    '<span itemprop="name">Testing - please ignore</span></h3>\r\n' +
    '<table cellpadding="0" cellspacing="0" border="0" summary="Event details" style="display:inline-table">\r\n' +
    '<tbody>\r\n' +
    '<tr>\r\n' +
    '<td valign="top" style="padding:0 1em 10px 0; font-family:Arial,Sans-serif; font-size:13px; color:#888; white-space:nowrap; width:90px">\r\n' +
    '<div><i style="font-style:normal">When</i></div>\r\n' +
    '</td>\r\n' +
    '<td valign="top" style="padding-bottom:10px; font-family:Arial,Sans-serif; font-size:13px; color:#222">\r\n' +
    '<div style="text-indent:-1px"><time itemprop="startDate" datetime="20191117T063000Z"></time><time itemprop="endDate" datetime="20191117T073000Z"></time>Sun Nov 17, 2019 12pm – 1pm\r\n' +
    '<span style="color:#888">India Standard Time - Kolkata</span></div>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '<tr>\r\n' +
    '<td valign="top" style="padding:0 1em 10px 0; font-family:Arial,Sans-serif; font-size:13px; color:#888; white-space:nowrap; width:90px">\r\n' +
    '<div><i style="font-style:normal">Joining info</i></div>\r\n' +
    '</td>\r\n' +
    '<td valign="top" style="padding-bottom:10px; font-family:Arial,Sans-serif; font-size:13px; color:#222">\r\n' +
    '<div style="text-indent:-1px"><span itemprop="potentialaction" itemscope="" itemtype="http://schema.org/JoinAction"><span itemprop="name"><span itemprop="target" itemscope="" itemtype="http://schema.org/EntryPoint"><span itemprop="url"><span itemprop="httpMethod"><a href="https://meet.google.com/tuw-oozo-ipx" target="_blank" style="color:#20c; white-space:nowrap">meet.google.com/tuw-oozo-ipx</a></span></span></span></span></span></div>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '<tr>\r\n' +
    '<td style="padding:0 1em 10px 0; font-family:Arial,Sans-serif; font-size:13px; color:#888; white-space:nowrap; width:90px">\r\n' +
    '</td>\r\n' +
    '<td>\r\n' +
    '<div style="text-indent:-1px">\r\n' +
    '<table cellspacing="0" cellpadding="0">\r\n' +
    '<tbody>\r\n' +
    '<tr>\r\n' +
    '<td valign="top" style="padding-bottom:10px; font-family:Arial,Sans-serif; font-size:13px; color:#222">\r\n' +
    '<div style="text-indent:-1px"><span style="color:#888">Or dial: <a href="tel:&#43;1 515-532-7530" target="_blank" style="color:#20c; white-space:nowrap">\r\n' +
    '<span itemprop="phoneNumber">&#43;1 515-532-7530</span></a><span itemprop="rtcPhoneNumberPassCodeLabel">&nbsp; PIN:</span><span itemprop="passCode"> 169995744#</span>&nbsp;\r\n' +
    '<a href="https://tel.meet/tuw-oozo-ipx?pin=1908432713267&amp;hs=0" target="_blank" style="color:#20c; white-space:nowrap">\r\n' +
    'More phone numbers</a></span></div>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '</tbody>\r\n' +
    '</table>\r\n' +
    '</div>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '<tr>\r\n' +
    '<td valign="top" style="padding:0 1em 10px 0; font-family:Arial,Sans-serif; font-size:13px; color:#888; white-space:nowrap; width:90px">\r\n' +
    '<div><i style="font-style:normal">Calendar</i></div>\r\n' +
    '</td>\r\n' +
    '<td valign="top" style="padding-bottom:10px; font-family:Arial,Sans-serif; font-size:13px; color:#222">\r\n' +
    '<div style="text-indent:-1px">prasanna@collab.ai</div>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '<tr>\r\n' +
    '<td valign="top" style="padding:0 1em 10px 0; font-family:Arial,Sans-serif; font-size:13px; color:#888; white-space:nowrap; width:90px">\r\n' +
    '<div><i style="font-style:normal">Who</i></div>\r\n' +
    '</td>\r\n' +
    '<td valign="top" style="padding-bottom:10px; font-family:Arial,Sans-serif; font-size:13px; color:#222">\r\n' +
    '<table cellspacing="0" cellpadding="0">\r\n' +
    '<tbody>\r\n' +
    '<tr>\r\n' +
    '<td style="padding-right:10px; font-family:Arial,Sans-serif; font-size:13px; color:#222; width:10px">\r\n' +
    '<div style="text-indent:-1px"><span style="font-family:Courier New,monospace">•</span></div>\r\n' +
    '</td>\r\n' +
    '<td style="padding-right:10px; font-family:Arial,Sans-serif; font-size:13px; color:#222">\r\n' +
    '<div style="text-indent:-1px">\r\n' +
    '<div>\r\n' +
    '<div style="margin:0 0 0.3em 0"><span itemprop="attendee" itemscope="" itemtype="http://schema.org/Person"><span itemprop="name" class="notranslate">ramesh.silveru@kore.com</span>\r\n' +
    '<meta itemprop="email" content="ramesh.silveru@kore.com">\r\n' +
    '</span><span itemprop="organizer" itemscope="" itemtype="http://schema.org/Person">\r\n' +
    '<meta itemprop="name" content="ramesh.silveru@kore.com">\r\n' +
    '<meta itemprop="email" content="ramesh.silveru@kore.com">\r\n' +
    '</span><span style="font-size:11px; color:#888"> - organizer</span></div>\r\n' +
    '</div>\r\n' +
    '</div>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '<tr>\r\n' +
    '<td style="padding-right:10px; font-family:Arial,Sans-serif; font-size:13px; color:#222; width:10px">\r\n' +
    '<div style="text-indent:-1px"><span style="font-family:Courier New,monospace">•</span></div>\r\n' +
    '</td>\r\n' +
    '<td style="padding-right:10px; font-family:Arial,Sans-serif; font-size:13px; color:#222">\r\n' +
    '<div style="text-indent:-1px">\r\n' +
    '<div>\r\n' +
    '<div style="margin:0 0 0.3em 0"><span itemprop="attendee" itemscope="" itemtype="http://schema.org/Person"><span itemprop="name" class="notranslate">prasanna@collab.ai</span>\r\n' +
    '<meta itemprop="email" content="prasanna@collab.ai">\r\n' +
    '</span></div>\r\n' +
    '</div>\r\n' +
    '</div>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '</tbody>\r\n' +
    '</table>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '</tbody>\r\n' +
    '</table>\r\n' +
    '<div style="float:right; font-weight:bold; font-size:13px"><a href="https://www.google.com/calendar/event?action=VIEW&amp;eid=MmIxZmgwdTgybmJpbmloOXQ2YjJxdW05Z2IgcHJhc2FubmFAY29sbGFiLmFp&amp;tok=MjMjcmFtZXNoLnNpbHZlcnVAa29yZS5jb20yNGU2MzNhZWQ0NjhiNjA0NWM5Mzg1Y2Y3MTk3MzljMDIzZmM1YzE2&amp;ctz=Asia%2FKolkata&amp;hl=en&amp;es=0" itemprop="url" style="color:#20c; white-space:nowrap">more\r\n' +
    ' details »</a><br>\r\n' +
    '</div>\r\n' +
    '</div>\r\n' +
    '<p style="color:#222; font-size:13px; margin:0"><span style="color:#888">Going (prasanna@collab.ai)?&nbsp;&nbsp;&nbsp;</span><wbr><strong><span itemprop="potentialaction" itemscope="" itemtype="http://schema.org/RsvpAction">\r\n' +
    '<meta itemprop="attendance" content="http://schema.org/RsvpAttendance/Yes">\r\n' +
    '<span itemprop="handler" itemscope="" itemtype="http://schema.org/HttpActionHandler"><link itemprop="method" href="http://schema.org/HttpRequestMethod/GET"><a href="https://www.google.com/calendar/event?action=RESPOND&amp;eid=MmIxZmgwdTgybmJpbmloOXQ2YjJxdW05Z2IgcHJhc2FubmFAY29sbGFiLmFp&amp;rst=1&amp;tok=MjMjcmFtZXNoLnNpbHZlcnVAa29yZS5jb20yNGU2MzNhZWQ0NjhiNjA0NWM5Mzg1Y2Y3MTk3MzljMDIzZmM1YzE2&amp;ctz=Asia%2FKolkata&amp;hl=en&amp;es=0" itemprop="url" style="color:#20c; white-space:nowrap">Yes</a></span></span><span style="margin:0 0.4em; font-weight:normal">\r\n' +
    ' - </span><span itemprop="potentialaction" itemscope="" itemtype="http://schema.org/RsvpAction">\r\n' +
    '<meta itemprop="attendance" content="http://schema.org/RsvpAttendance/Maybe">\r\n' +
    '<span itemprop="handler" itemscope="" itemtype="http://schema.org/HttpActionHandler"><link itemprop="method" href="http://schema.org/HttpRequestMethod/GET"><a href="https://www.google.com/calendar/event?action=RESPOND&amp;eid=MmIxZmgwdTgybmJpbmloOXQ2YjJxdW05Z2IgcHJhc2FubmFAY29sbGFiLmFp&amp;rst=3&amp;tok=MjMjcmFtZXNoLnNpbHZlcnVAa29yZS5jb20yNGU2MzNhZWQ0NjhiNjA0NWM5Mzg1Y2Y3MTk3MzljMDIzZmM1YzE2&amp;ctz=Asia%2FKolkata&amp;hl=en&amp;es=0" itemprop="url" style="color:#20c; white-space:nowrap">Maybe</a></span></span><span style="margin:0 0.4em; font-weight:normal">\r\n' +
    ' - </span><span itemprop="potentialaction" itemscope="" itemtype="http://schema.org/RsvpAction">\r\n' +
    '<meta itemprop="attendance" content="http://schema.org/RsvpAttendance/No">\r\n' +
    '<span itemprop="handler" itemscope="" itemtype="http://schema.org/HttpActionHandler"><link itemprop="method" href="http://schema.org/HttpRequestMethod/GET"><a href="https://www.google.com/calendar/event?action=RESPOND&amp;eid=MmIxZmgwdTgybmJpbmloOXQ2YjJxdW05Z2IgcHJhc2FubmFAY29sbGFiLmFp&amp;rst=2&amp;tok=MjMjcmFtZXNoLnNpbHZlcnVAa29yZS5jb20yNGU2MzNhZWQ0NjhiNjA0NWM5Mzg1Y2Y3MTk3MzljMDIzZmM1YzE2&amp;ctz=Asia%2FKolkata&amp;hl=en&amp;es=0" itemprop="url" style="color:#20c; white-space:nowrap">No</a></span></span></strong>&nbsp;&nbsp;&nbsp;&nbsp;<wbr><a href="https://www.google.com/calendar/event?action=VIEW&amp;eid=MmIxZmgwdTgybmJpbmloOXQ2YjJxdW05Z2IgcHJhc2FubmFAY29sbGFiLmFp&amp;tok=MjMjcmFtZXNoLnNpbHZlcnVAa29yZS5jb20yNGU2MzNhZWQ0NjhiNjA0NWM5Mzg1Y2Y3MTk3MzljMDIzZmM1YzE2&amp;ctz=Asia%2FKolkata&amp;hl=en&amp;es=0" itemprop="url" style="color:#20c; white-space:nowrap">more\r\n' +
    ' options »</a></p>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '<tr>\r\n' +
    '<td style="background-color:#f6f6f6; color:#888; border-top:1px Solid #ccc; font-family:Arial,Sans-serif; font-size:11px">\r\n' +
    '<p>Invitation from <a href="https://www.google.com/calendar/" target="_blank" style="">\r\n' +
    'Google Calendar</a></p>\r\n' +
    '<p>You are receiving this courtesy email at the account prasanna@collab.ai because you are an attendee of this event.</p>\r\n' +
    '<p>To stop receiving future updates for this event, decline this event. Alternatively you can sign up for a Google account at https://www.google.com/calendar/ and control your notification settings for your entire calendar.</p>\r\n' +
    '<p>Forwarding this invitation could allow any recipient to send a response to the organizer and be added to the guest list, or invite others regardless of their own invitation status, or to modify your RSVP.\r\n' +
    '<a href="https://support.google.com/calendar/answer/37135#forwarding">Learn More</a>.</p>\r\n' +
    '</td>\r\n' +
    '</tr>\r\n' +
    '</tbody>\r\n' +
    '</table>\r\n' +
    '</div>\r\n' +
    '</span></span>\r\n' +
    '</body>\r\n' +
    '</html>\r\n'
}



/*async function parseMail(message){
  const $ = cheerio.load(message.content);
  for(i=0; i<$('time').length;i++){
  	var timeTag = $('time')[i];
    if(timeTag && timeTag.attribs && timeTag.attribs.itemprop){
      if(timeTag.attribs.itemprop == 'startDate'){
        console.log("--------------------------START DATE",timeTag.attribs.datetime,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");
      }
      if(timeTag.attribs.itemprop == 'endDate'){
        console.log("--------------------------END DATE",timeTag.attribs.datetime,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");
      }
    }
  };
  //console.log($('span'));
  for(i=0;i<$('span').length;i++){
  	var spanTag = $('span')[i]
  	//console.log(spanTag.attribs)
  	if(spanTag&&spanTag.attribs&&spanTag.attribs.itemprop == "phoneNumber"){
  		console.log(i,spanTag.children[0].data)
  	}
  	if(spanTag&&spanTag.attribs&&spanTag.attribs.itemprop == "passCode"){
  		console.log(i,spanTag.children[0].data)
  	}
  }
}

/*const $ = cheerio.load(body.content);

console.log($("a").length);*/

//parseMail(body);*/















    /*const request = require("request");
    const fs = require("fs");

      var options = {
        url:"https://api.twilio.com/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX27/Recordings/RE30b87325cee9fcedddbf6b39cc66adbc",
        method: 'GET',
        agent: false
      };

      request(options,function(err,res){
        //console.log(res);
        res.setEncoding('binary');
        console.log(res)
        var mp3data = '';
        res.on(res.body, function (chunk) {
            mp3data += chunk;
        });

        var fileName = "/home/rameshsilveru/Desktop/KORA/ScheduleMeeting/results.wav";
        fs.writeFile(fileName, mp3data, 'binary', function(err){
            if(err){
                return console.log(err);
            }else{
                console.log("File Saved");
            }
        });
    });
*/
 const fs = require('fs');
const download = require('download');
 
 
download('https://api.twilio.com/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX27/Recordings/RE4591a87970e97b3480944e0ae82fb539.wav').then(data => {
    fs.writeFileSync('/home/rameshsilveru/Desktop/KORA/ScheduleMeeting/Asr/audio.wav', data);
});
 
      
