const Redis 	= require('ioredis');
const process 	= require("./process.js");

function createClient(redisConfig){
	const client = new Redis(process.REDIS_CONFIG);

	client.on('connect', function() {
	  console.log('Redis client connected');
	});

	client.on('error', function(err) {
	  console.log('Something went wrong ' + err);
	});

	return client;
}

module.exports = {
	"createClient" : createClient
}