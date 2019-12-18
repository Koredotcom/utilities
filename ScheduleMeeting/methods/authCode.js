const {getAuthToken} = require("./authToken.js");

function getAuthCode(req,res){
	console.log(req.query)
	if(req.query.code && req.query.state){
		return getAuthToken(req, res, req.query.code, req.query.state);
	}else{
		res.status(400);
        res.send({message: 'Request to get auth code failed'});
	}
}

module.exports = {
	"getAuthCode" : getAuthCode
}