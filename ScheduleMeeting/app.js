const express 		  = require('express');
const logger 		  = require('morgan');
const bodyParser      = require('body-parser');
const process		  = require("./process.js");
const routes		  =	require("./routes/index.js");
const app 			  = express();
const mongoose	 	  = require("mongoose");
const {twilioRecord}      = require("./Twilio/recording.js");

//twilioRecord("https://api.twilio.com/2010-04-01/Accounts/ACcea0991dae7309b636cbbc26e1eeff27/Recordings/RE3688b944c50dc998ce5d39621bea814c")

let connectionUrl       = "mongodb://localhost:27017/"+process.MONGO.NAME;
mongoose.connect(connectionUrl,{ useNewUrlParser: true });

app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded());
app.use("/",routes);

const PORT = process.PORT || '3000';

app.listen(PORT,function(){
	console.log("Server running on port ", PORT);
});
