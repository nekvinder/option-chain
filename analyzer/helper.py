import requests
import os
import json
import sqlite3

enableCache = True
cacheReq = sqlite3.connect("cacheReqs.db")
cur = cacheReq.cursor()


def createTable():
    cur.execute("CREATE TABLE IF NOT EXISTS data (date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL)")


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
