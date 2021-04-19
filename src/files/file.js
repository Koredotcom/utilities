var FormData = require('form-data');
var fs = require('fs');
var fetch = require('node-fetch')
var config = require('../config.json');

const AEM_UPDATED = "AEM_UPDATED";
const AEM_NEW = "AEM_NEW";
const AEM_DELETED = "AEM_DELETED";
const kg_qa = {
    "2": { "question": "Why is my unified estate workflow for an Individual Retirement Account (IRA) request getting rejected? ", "botInfo": { "botName": "MS Estate Account BOT", "concept": "Individual Retirement Account (IRA)" } },
};

const add_questions = async (faqs_map, questionInfo, kg_root_node_name) => {
    let faq_quest_templ_new = {
        "question": "",
        "alternateQuestions": [],
        "terms": [
            kg_root_node_name
        ],
        "tags": [],
        "responseType": "message",
        "answer": [
            {
                "text": "1",
                "type": "basic",
                "channel": "default"
            }
        ],
        "alternateAnswers": []
    }

    faq_quest_templ_new.question = questionInfo.question;

    if (questionInfo.action !== undefined) {
        faq_quest_templ_new.terms = [questionInfo.kmId, questionInfo.action, kg_root_node_name];
    } else {

    }
    faq_quest_templ_new.answer[0].text = questionInfo.answer
    faqs_map[questionInfo.kmId]=faq_quest_templ_new;
}
const update_faqs = async (aem_question_set, kg_root_node_name, faqs) => {
    const faqs_map = {};
    Object.keys(faqs).forEach(key => {
        faqs_map[faqs[key].terms[0]] = faqs[key];
    })

    let questionInfo = {};
    for (const key in aem_question_set) {
        if (aem_question_set.hasOwnProperty(key)) {
            const question_set = aem_question_set[key];
            let action = ""
            if (question_set.action == "update") {
                action = AEM_UPDATED;
            } else if (question_set.action == "new") {
                action = AEM_NEW
            } else if (question_set.action == "deleted") {
                action = AEM_DELETED
            } else {

            }
            if (action !== "") {
                questionInfo = { "question": question_set.question, "answer": question_set.answer, "action": action, "kmId": question_set.kmId }
                add_questions(faqs_map, questionInfo, kg_root_node_name)
            }
        }
    }
      faqs_result=[]
    Object.keys(faqs_map).forEach(key=>{
        faqs_result.push(faqs_map[key]);
    })
    console.log("---------------test-------",faqs_result);
    return { faqs:faqs_result };
}
const get_file_data = async (path) => {
    return new Promise(function (resolve, reject) {
        fs.readFile(path, async function (err, data) {
            if (err) throw err;
            data = JSON.parse(data);
            return resolve(data)
        });
    });
}

async function upload_file(input) {
    const fd = new FormData()
    if (!fs.existsSync(input)) {
        throw new Error("Please provide the file to upload - " + input);
    }
    fd.append('file', fs.createReadStream(input))
    fd.append('fileContext', "bulkImport")
    fd.append('fileExtension', "json")

    var headers = { ...fd.headers }
    headers["auth"] = config.JWT
    const options = {
        method: 'post',
        body: fd,
        headers: headers
    }

    return fetch(config.FILE_IMPORT_URL, options).then(res => res.json())
        .then(json => json.fileId);

}

module.exports = { get_file_data, update_faqs, upload_file }
