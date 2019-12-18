const {getMail} = require('./mail.js');

const notification = async (req, res) => {
  console.log(req.body)
  if (req.query && req.query.validationtoken) {
    res.status(200);
    res.send(req.query.validationtoken);
  } else {
    if (req.body && req.body.value && req.body.value[0] && req.body.value[0].ResourceData && req.body.value[0].ResourceData.Id) {
      const messageId = req.body.value[0].ResourceData.Id;
      console.log("-------",messageId,"============")
      try {
        await getMail(messageId);
        console.log('Executed........');
        res.status(202);
        res.send('202 - Accepted');
      } catch (error) {
        console.log(error);
        res.status(202);
        res.send('202 - Accepted');
      }
    } else {
      console.log('Under else condition');
      res.status(202);
      res.send('202 - Accepted');
    }
  }
};

module.exports = 
{
"notification":notification
}
