var { import_bot } = require('../import/bot_import.js')
var { export_bot } = require('../export/bot_export.js');
var { send_mail } = require('../email/email.js');
var { get_file_data, update_faqs } = require('../files/file.js')
var config = require('../config.json');

const update_aem_bot = async (req) => {
    try {
        await export_bot();
        const botDefResponse = await get_file_data(config.BOT_DEF_FILE_LOC);
        const knowledgeTasks = botDefResponse.knowledgeTasks[0];
        //console.log(req.body)
        console.log('--Bot name --',knowledgeTasks['taxonomy'][0]['label'])
        const { faqs } = await update_faqs(req.body, knowledgeTasks['taxonomy'][0]['label'],knowledgeTasks.faqs.faqs);
       // console.log("faqs---->", faqs);
      await import_bot(faqs);
        // await send_mail(faqs.toString());
        return { "success": true }
    } catch (e) {
        console.log(e);
        return { "success": false }
    }
}

module.exports = { update_aem_bot }
