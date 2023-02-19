import requests
import datetime
import os
import json
import sqlite3

enableCache = True
cacheReq = sqlite3.connect("cacheReqs.db")
cur = cacheReq.cursor()


def createTableIfNotExists():
    cur.execute("CREATE TABLE IF NOT EXISTS data (date DATE,day date, countCall REAL, countPut REAL)")


createTableIfNotExists()


def insertIntoTable(date, call, put):
    today = datetime.date.today()
    cur.execute("INSERT INTO data VALUES (?,?, ?, ?)", (date, today, call, put))
    cacheReq.commit()


def getCallPutHistoryToday():

    # get todays dated data
    cur.execute("SELECT * FROM data WHERE day = date('now')")
    todaysData = cur.fetchall()
    print(todaysData)
    return todaysData

    # cur.execute("SELECT * FROM data")
    # return cur.fetchall()


def printProgressBar(iteration, total, prefix="", suffix="", decimals=1, length=100, fill="█", printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def getJson(url, cookies=None):
    if enableCache:
        urlAsFileName = url.replace("/", "_")
        fileExists = os.path.isfile(f"cache/{urlAsFileName}.json")
        if fileExists:
            with open(f"cache/{urlAsFileName}.json", "r") as f:
                json_obj = json.load(f)
                return json_obj

    baseurl = "https://www.nseindia.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    }
    session = requests.Session()
    if not cookies:
        request = session.get(baseurl, headers=headers, timeout=100)
        cookies = dict(request.cookies)
    response = session.get(url, headers=headers, timeout=30, cookies=cookies)
    json_obj = response.json()

    if enableCache:
        with open(f"cache/{urlAsFileName}.json", "w") as f:
            json.dump(json_obj, f)

    return json_obj


def sendEmail(BODY_HTML):
    import boto3
    from botocore.exceptions import ClientError

    SENDER = "nekAnalyzer <nekvinder@gmail.com>"
    RECIPIENT = "rocksukhvinder@gmail.com"
    AWS_REGION = "ap-south-1"
    SUBJECT = "Analysis Bot"
    BODY_TEXT = "Err code 126"
    CHARSET = "UTF-8"
    client = boto3.client("ses", region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    RECIPIENT,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": BODY_HTML,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])
