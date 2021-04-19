const express = require('express');
const bodyParser = require('body-parser')
const { update_aem_bot } = require('./aem/aem.js');
const app = express();

app.use(bodyParser.json())
app.post('/aem/update', async function (req, res) {
    const response = await update_aem_bot(req)
    res.json(response);
})

app.listen(8081, function (req, res) {
    console.log("AEM service started success fully");
})