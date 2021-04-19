const nodemailer = require("nodemailer");
var config = require('../config.json');

async function send_mail(effectedBots) {
  const transporter = nodemailer.createTransport(config.SMPT.TRANSPORT);
  let info = await transporter.sendMail({
    ...config.SMPT.MAIL,
    html:  get_mail_template()
  });
  console.log("Message sent: %s", info.messageId);
  console.log("Preview URL: %s", nodemailer.getTestMessageUrl(info));

  function get_mail_template() {
    return "<h2>AEM Updates<\/h2>\r\n\r\n<table>\r\n  <tr>\r\n    <td>Bot builder Url : <\/td>\r\n    <td>https:\/\/bots.kore.ai\/botbuilder<\/td>\r\n  <\/tr>\r\n  <tr>\r\n    <td>Effected Bots : <\/td>\r\n    <td>" + effectedBots + "<\/td>\r\n  <\/tr>\r\n  <tr>\r\n    <td>Aem dump bot : <\/td>\r\n    <td>MS AEM_DUMP<\/td>\r\n  <\/tr>\r\n<\/table>\r\n";
  }
}
module.exports = { send_mail };
