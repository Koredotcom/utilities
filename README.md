#Install dependencies
```
src> pip3 install -r requirements.txt
```
# Run the application
```
src>python3 app.py
```
# Add Testcases :
## Requst:
```
http://127.0.0.1:5000/testcase/add [POST]
```
## Multi turn example:
```
{
        "messages": [
            {
                "input": "529 account",
                "outputs": [
                    {
                        "contains": "Reopen 529 Account"
                    }
                ]
            },
            {
                "input": "reopen 529 Account",
                "outputs": [
                    {
                        "contains": "Ans: How do I reopen a 529 account?"
                    }
                ]
            }
        ]
    }
```
## Single turn questions
```
{
        "messages": [
            {
                "input": "Open estate account",
                "outputs": [
                    "Ans: How do I open an estate account?"
                ]
            }
        ]
    }
```
# Run the testcases
```
http://127.0.0.1:5000/run[GET]
```
# Get all test cases:
```
http://127.0.0.1:5000/testcase/get/all
```
# Get the testResult
```
http://127.0.0.1:5000/testResult
```
#Test results as XLS
```
Check the XLS inside src/TestResults
```
