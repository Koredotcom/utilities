var axios = require('axios');
var fs = require('fs');
var Path = require('path');
var AdmZip = require('adm-zip');
var config = require('../config.json');

const botId = config.botId;
const JWT = config.JWT
const BOT_EXPORT_URL = `${config.BASE_URL}${botId}${config.EXPORT_URL}`;
const BOT_EXPORT_STATUS = `${config.BASE_URL}${botId}${config.EXPORT_STATUS_URL}`;

const extract_zip = async () => {
    var zip = new AdmZip(config.ZIP_LOC)
    var zipEntries = zip.getEntries();
    if (!fs.existsSync(config.EXTRACT_LOC)) {
        fs.mkdirSync(config.EXTRACT_LOC);
    }
    zipEntries.forEach(function (zipEntry) {
        try {
            fs.writeFileSync(config.EXTRACT_LOC + zipEntry.entryName, zipEntry.getData().toString('utf-8'))
        } catch (e) {
            console.log(e)
        }
    });
}

const download_zip = async (url) => {
    const path = Path.resolve("./", config.ZIP_LOC)
    const writer = fs.createWriteStream(path)

    const response = await axios({
        url,
        method: 'GET',
        responseType: 'stream'
    })

    response.data.pipe(writer)

    return new Promise((resolve, reject) => {
        writer.on('finish', resolve)
        writer.on('error', reject)
    })
}

const export_bot = async () => {
    let bot_export_response = []
    let headers = {
        'auth': JWT,
        'content-type': 'application/json'
    }
    const data = {
        "exportType": "latest",
        "exportOptions": {
            "tasks": ["knowledgeGraph"]
        }

    };
    bot_export_response = await axios.post(BOT_EXPORT_URL, data, { headers: headers });
    console.log(bot_export_response.data);
    const bot_file_url = await axios.get(BOT_EXPORT_STATUS, { headers: headers });
    console.log(bot_file_url.data.downloadURL)
    await download_zip(bot_file_url.data.downloadURL)
    await extract_zip()

    return bot_export_response;
}

module.exports = { export_bot }
