var fs = require('fs');
var axios = require('axios');
var config = require('../config.json');
var {get_file_data,upload_file} = require('../files/file.js')

const update_bot_def = async (faqs) => {
    const botDefResponse = await get_file_data(config.BOT_DEF_FILE_LOC);
    botDefResponse.knowledgeTasks[0].faqs.faqs = faqs;
    const data = JSON.stringify(botDefResponse).toString('utf-8')
    fs.writeFileSync(config.BOT_DEF_FILE_LOC, data, (err) => {
        if (err)
            console.log(err);
        else {
            console.log("File written successfully\n");
        }
    });
}

const import_bot_into_existing_bot = async (botDefFileId, configFileId) => {

    const headers = {
        "auth": config.JWT,
        "Content-Type": "application/json"
    }
    const data = {
        "botDefinition": botDefFileId,
        "configInfo": configFileId

    }
    const EXISTING_BOT_IMPORT = `${config.BASE_URL}${config.botId}${config.IMPORT_URL}`;
    const response = await axios.post(EXISTING_BOT_IMPORT, data, { headers: headers })
    return response;
}

const import_bot = async (faqs) => {
    await update_bot_def(faqs);
    const botDefFileId = await upload_file(config.BOT_DEF_FILE_LOC)
    const botConfigFileId = await upload_file(config.BOT_CONFIG_FILE_LOC)
    const response = await import_bot_into_existing_bot(botDefFileId, botConfigFileId)
    console.log("Bot imported success fully - ", response.data);
    return response.data;
}

module.exports = { import_bot }
