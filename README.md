# Custom PDF Extraction


## Pre-requisites
* **Python 2.7:** 
1. This utlility requires python 2.7, please download it from here: https://www.python.org/downloads/
2. Downloading and installing python is OS specific, you can follow any other download and installation procedure available in internet

* **Virtual Environment:** 
1. It is advised to use virtual environment, instead of directly installing requirements in the system directly. Follow the steps mentioned here to setup virtual environment. https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/

* **ngrok:**
1. Download ngrok from this link based on your OS https://ngrok.com/download

## Installation Steps
1. Clone the repository with following command 
`git clone https://github.com/Koredotcom/utilities.git`

2. Checkout `custom_pdf_extraction` branch using following command `git checkout custom_pdf_extraction`

2. Activate the virtual environment. Instructions for activating are present in the installation link 

3. Install the requirements with following command
`pip install -r requirements.txt`

4. Run the following command to start the server `python start_server.py`


## Make a extraction request
1. Open terminal from the location, where pdf files are present.
2. Run following command to start a http server with that directory to host pdf files

    a. `python3 -m http.server` for starting a http server using python3
    
    b. `python -m SimpleHTTPServer` for starting a http server using python2
    
3. Open terminal at downloaded ngrok tool location
4. Run following command `ngrok http <PORT NUMBER>`, port number here is the port with which http server is started in above step.
5. Sample curl  -
<br> ```curl -H "Content-Type: application/json" -H "Authorization: b" http://localhost:5001/pdf_extraction/extract -d '{"fileUrl": "http://97ab6a930c50.ngrok.io/sample.pdf","type":"e_ms","extractionID":"et-12D3"}'```
6. extractionID parameter can be left as it is, for local testing.  
6. Hit the curl with required parameters.

7. Logs can be observed in `/var/www/logs/Extraction.log`