var request = require("request");

function getGraphToken(){
  var options = { method: 'POST',
    url: 'https://login.microsoftonline.com/027e2e03-351b-4dbb-be47-c74938f744aa/oauth2/v2.0/token',
    headers: 
     { 'postman-token': 'c31d410f-730d-c1e6-1950-4c1449962c89',
       'cache-control': 'no-cache',
       'content-type': 'application/x-www-form-urlencoded' },
    form: 
     { client_id: 'e5ef7b9c-14a0-4179-b32e-474e11397c75',
       scope: 'offline_access%20User.Read%20Mail.Read',
       code: 'OAQABAAIAAACQN9QBRU3jT6bcBQLZNUj7b3VrxGUyWOI3Cm9YWSLzw6LEDvNxfSrNyYHU5xSKWyHbmy6jRTx600FfoYLje2xvwDvZniUyBkN8wqwO7Z8MmM5R9Z2WfwvhaIjSe0HXBUy5bnr42QqL18zj09R-nDQ9zccjP5kEfFe6210xMpInRhtEDk3j1iVq8Xew5cGrPUb_faXv_78QpdNzMnUYO7jlIuMcJ2fP5w98IehqihB1ZaakZ7ARbIMkikZryrVasFhQzKK8j4tKK48kQDaCh8sEHMOQk4i5dlUQDhYul0JhZJRQC82syD8nhcNyp7iEAF56n02_TQ3dbr18QMmN1re2fGdTldUhtb-sBFeyX2oGb-BmcqkH6WqWx2v01fNyqz--Qw2-86_nZvaJlu3KwAdFKalG5zU28gVthzCDmY4E_yXPqNTC5d0qcL-FPaJv1lAal9M7VwrfvKdBBEvRd3qycjDwQ2bJRuSWYLRPFYxWZOLgU6AhJ7BooiTpeanf-wJZrNzTZUelgVM0XkcOy1gGRAyJRbYebv-NqhXA8L3PnkXvqE4sMVHbwdtiIJs4kPix59OCx953HbGMKRL4F_SkeUiQdlK67zMd37GkEz-MfK1L4Jb_byKh_ix6eUG-klxZHiLtVcudIIavHRaAnF6HIAA',
       redirect_uri: 'http://localhost:3000/getAuthCode',
       grant_type: 'authorization_code',
       client_secret: 'Yn=JL6fye0-uvo:]RQW6mxQ30ec5yrqd' } };

  request(options, function (error, response, body) {
    if (error) throw new Error(error);

    console.log(body);
  });
}


function getOutlookToken(){
  var options = { method: 'POST',
    url: 'https://login.microsoftonline.com/027e2e03-351b-4dbb-be47-c74938f744aa/oauth2/v2.0/token',
    headers: 
     {
       'content-type': 'application/x-www-form-urlencoded' 
     },
    form: 
     { client_id: 'e5ef7b9c-14a0-4179-b32e-474e11397c75',
       scope: 'https://outlook.office.com/mail.read',
       code: 'OAQABAAIAAACQN9QBRU3jT6bcBQLZNUj7taXPHUxM0bjQ-BVTTe8YGc5LADG1RDq4R3PtHQ9qtGOYH3lD1SISa3gm7NIs-v2Fg6ifeTa1Wpnq1SBztVTHGofOpB6QOZrax5TVHsrANBD0wDFp0tloIXzfamlk3H_GDERaC6DMIcGvek4WcF-lxTCPtW3RItrt9SUkaHVswzSIhjy0_FJO9yx_SD6IdYAsLK7w_1sfhHoN-PiyixnpLg-4rGoFvXuYefZFthFLjpvtmzoRUGC7IaY7ZRRn7CLREhDivEsZME74zz8nogRH815MwCDn4th9uNux0vtXV9YVbt64SXvA_Wekzfv0BldGflz32TQkKKUqKQay25y_lv-94Gg9X-aaXoEwTdKwjgPEiXfQDn9OGiukMP2hVKVwWbgUhctQZhhvtVt58NFgkZcc1XjyRGq52w01l5OhyWOhdtKUg0F13BAiMeQoXF2TLOllGWa3JFiBu0N5dYQJHeGyN_hGzSFmFBICaObMThpgK4chmuBV4gJvClEgDAFS86p88mIwTeUikjD6n_2E1vNjpYP6BC-xws5qtNGVbBMefet3CfkpuqFYG8R10lNJ4nTXOvhl78pX215yuRcrbCAA',
       redirect_uri: 'http://localhost:3000/getAuthCode',
       grant_type: 'authorization_code',
       client_secret: 'Yn=JL6fye0-uvo:]RQW6mxQ30ec5yrqd' } };

  request(options, function (error, response, body) {
    if (error) throw new Error(error);
    console.log(body);
  });
}


