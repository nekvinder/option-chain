import os
import time
from tabulate import tabulate
import datetime
import urllib.parse
import boto3
from botocore.exceptions import ClientError

from terminaltables import AsciiTable
import requests

indicesUrl = "https://www.nseindia.com/api/option-chain-indices?symbol="
equitiesUrl = "https://www.nseindia.com/api/option-chain-equities?symbol="

cookies = None


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


def getJson(url):
    global cookies
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
    # print("Calling url: " + url + " with cookies: " + str(cookies))
    response = session.get(url, headers=headers, timeout=30, cookies=cookies)
    # print("Got response from url: " + url)
    json_obj = response.json()
    # print("Response: " + str(json_obj))

    return json_obj


def getStockList():
    try:
        return getJson("https://www.nseindia.com/api/master-quote")["data"]
    except:
        # print("Error in getting stock list, using local list")
        return [
            "AARTIIND",
            "ABB",
            "ABBOTINDIA",
            "ABCAPITAL",
            "ABFRL",
            "ACC",
            "ADANIENT",
            "ADANIPORTS",
            "ALKEM",
            "AMBUJACEM",
            "APOLLOHOSP",
            "APOLLOTYRE",
            "ASHOKLEY",
            "ASIANPAINT",
            "ASTRAL",
            "ATUL",
            "AUBANK",
            "AUROPHARMA",
            "AXISBANK",
            "BAJAJ-AUTO",
            "BAJAJFINSV",
            "BAJFINANCE",
            "BALKRISIND",
            "BALRAMCHIN",
            "BANDHANBNK",
            "BANKBARODA",
            "BATAINDIA",
            "BEL",
            "BERGEPAINT",
            "BHARATFORG",
            "BHARTIARTL",
            "BHEL",
            "BIOCON",
            "BOSCHLTD",
            "BPCL",
            "BRITANNIA",
            "BSOFT",
            "CANBK",
            "CANFINHOME",
            "CHAMBLFERT",
            "CHOLAFIN",
            "CIPLA",
            "COALINDIA",
            "COFORGE",
            "COLPAL",
            "CONCOR",
            "COROMANDEL",
            "CROMPTON",
            "CUB",
            "CUMMINSIND",
            "DABUR",
            "DALBHARAT",
            "DEEPAKNTR",
            "DELTACORP",
            "DIVISLAB",
            "DIXON",
            "DLF",
            "DRREDDY",
            "EICHERMOT",
            "ESCORTS",
            "EXIDEIND",
            "FEDERALBNK",
            "FSL",
            "GAIL",
            "GLENMARK",
            "GMRINFRA",
            "GNFC",
            "GODREJCP",
            "GODREJPROP",
            "GRANULES",
            "GRASIM",
            "GUJGASLTD",
            "HAL",
            "HAVELLS",
            "HCLTECH",
            "HDFC",
            "HDFCAMC",
            "HDFCBANK",
            "HDFCLIFE",
            "HEROMOTOCO",
            "HINDALCO",
            "HINDCOPPER",
            "HINDPETRO",
            "HINDUNILVR",
            "HONAUT",
            "IBULHSGFIN",
            "ICICIBANK",
            "ICICIGI",
            "ICICIPRULI",
            "IDEA",
            "IDFC",
            "IDFCFIRSTB",
            "IEX",
            "IGL",
            "INDHOTEL",
            "INDIACEM",
            "INDIAMART",
            "INDIGO",
            "INDUSINDBK",
            "INDUSTOWER",
            "INFY",
            "INTELLECT",
            "IOC",
            "IPCALAB",
            "IRCTC",
            "ITC",
            "JINDALSTEL",
            "JKCEMENT",
            "JSWSTEEL",
            "JUBLFOOD",
            "KOTAKBANK",
            "L&TFH",
            "LALPATHLAB",
            "LAURUSLABS",
            "LICHSGFIN",
            "LT",
            "LTIM",
            "LTTS",
            "LUPIN",
            "M&M",
            "M&MFIN",
            "MANAPPURAM",
            "MARICO",
            "MARUTI",
            "MCDOWELL-N",
            "MCX",
            "METROPOLIS",
            "MFSL",
            "MGL",
            "MOTHERSON",
            "MPHASIS",
            "MRF",
            "MUTHOOTFIN",
            "NATIONALUM",
            "NAUKRI",
            "NAVINFLUOR",
            "NESTLEIND",
            "NMDC",
            "NTPC",
            "OBEROIRLTY",
            "OFSS",
            "ONGC",
            "PAGEIND",
            "PEL",
            "PERSISTENT",
            "PETRONET",
            "PFC",
            "PIDILITIND",
            "PIIND",
            "PNB",
            "POLYCAB",
            "POWERGRID",
            "PVR",
            "RAIN",
            "RAMCOCEM",
            "RBLBANK",
            "RECLTD",
            "RELIANCE",
            "SAIL",
            "SBICARD",
            "SBILIFE",
            "SBIN",
            "SHREECEM",
            "SHRIRAMFIN",
            "SIEMENS",
            "SRF",
            "SRTRANSFIN",
            "SUNPHARMA",
            "SUNTV",
            "SYNGENE",
            "TATACHEM",
            "TATACOMM",
            "TATACONSUM",
            "TATAMOTORS",
            "TATAPOWER",
            "TATASTEEL",
            "TCS",
            "TECHM",
            "TITAN",
            "TORNTPHARM",
            "TORNTPOWER",
            "TRENT",
            "TVSMOTOR",
            "UBL",
            "ULTRACEMCO",
            "UPL",
            "VEDL",
            "VOLTAS",
            "WHIRLPOOL",
            "WIPRO",
            "ZEEL",
            "ZYDUSLIFE",
        ]


def getData(sym, isIndex=False):
    result = {"sym": sym}

    searchRecordsCount = 5
    json_obj = getJson(indicesUrl + sym) if isIndex else getJson(equitiesUrl + sym)
    # print(sym, json_obj)
    underlying_value = json_obj["records"]["underlyingValue"]

    # put
    splitIndex = 0
    for i in range(len(json_obj["filtered"]["data"])):
        if json_obj["filtered"]["data"][i]["strikePrice"] > underlying_value:
            splitIndex = i
            break
    res = []
    for i in range(splitIndex - searchRecordsCount, splitIndex):
        openInterestPut = json_obj["filtered"]["data"][i]["PE"]["openInterest"]
        strikePrice = json_obj["filtered"]["data"][i]["strikePrice"]
        res.append((strikePrice, openInterestPut))
    resSortedOnOI = sorted(res, key=lambda x: x[1], reverse=True)
    result["put"] = resSortedOnOI[0][0]

    # call
    res = []
    for i in range(splitIndex, splitIndex + searchRecordsCount):
        openInterestPut = json_obj["filtered"]["data"][i]["CE"]["openInterest"]
        strikePrice = json_obj["filtered"]["data"][i]["strikePrice"]
        res.append((strikePrice, openInterestPut))
    resSortedOnOI = sorted(res, key=lambda x: x[1], reverse=True)
    result["call"] = resSortedOnOI[0][0]

    result["currentValue"] = underlying_value
    putDiff = result["put"] - underlying_value
    callDiff = result["call"] - underlying_value
    if abs(putDiff) < abs(callDiff):
        result["analysisType"] = "put"
        result["analysisValue"] = round(abs(putDiff), 3)
    else:
        result["analysisType"] = "call"
        result["analysisValue"] = round(abs(callDiff), 3)

    if "IS_AWS_LAMBDA" in os.environ:
        print("Done for", sym)

    return result


def getAnalysis(isIndex=True):
    printStr = ""
    if isIndex:
        stockList = ["NIFTY", "BANKNIFTY"]
    else:
        stockList = getStockList()[:5]

    res = []
    prefix = "Progress: Index" if isIndex else "Progress: Equity"
    printProgressBar(0, len(stockList), prefix=prefix, suffix="Complete", length=50)

    for stock in stockList:
        printProgressBar(stockList.index(stock) + 1, len(stockList), prefix=prefix, suffix="Complete", length=50)
        try:
            res.append(getData(urllib.parse.quote(stock), isIndex=isIndex))
        except Exception as e:
            print("Error for", stock, e)

    # sort res based on analysisValue
    res = [i for i in res if i is not None]
    res = sorted(res, key=lambda x: x["analysisValue"])

    linkRef = f"https://in.tradingview.com/chart/?symbol=NSE%3A"

    tableHeader = ["Stock", "Put OI", "Current", "Call OI", "Analysis", "Analysis Value", "Link"]
    tableData = []
    for r in res:
        tableData.append([r["sym"], r["put"], r["currentValue"], r["call"], r["analysisType"], r["analysisValue"], f'<a target="_" href="{linkRef + r["sym"]}">Chart</a>'])
        printStr += f"\nStock: {r['sym']} | {r['put']}  {r['currentValue']}  {r['call']} | {r['analysisType']}:{r['analysisValue']}"

    table = AsciiTable(tableData)
    htmlTable = tabulate(tableData, headers=tableHeader, tablefmt="unsafehtml")
    return "<center>" + htmlTable + "</center>"

    # return table.table


def lambda_handler(event, context):
    data = getAnalysis()
    SENDER = "nekvinder-bot-stocks <nekvinder@gmail.com>"
    RECIPIENT = "goesdeeper@protonmail.com"
    # CONFIGURATION_SET = "ConfigSet"
    AWS_REGION = "ap-south-1"
    SUBJECT = "Stocks Option chain analysis"
    BODY_TEXT = data
    BODY_HTML = f"""<html> <head></head> <body> {data} </body> </html> """
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
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])


if __name__ == "__main__":

    while True:
        table = getAnalysis()
        minutesSleep = 15
        indexTable = getAnalysis(isIndex=False)
        # write to a file names YYYYMMDDHHMMSS.txt
        currentTime = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        for filename in [currentTime + ".html", "latest.html"]:
            with open(filename, "w") as f:
                f.write(f"<center><h4>Last Update At: {datetime.datetime.now().strftime('%Y %m %d - %H:%M:%S')}</h4></center>")
                f.write(table + "\n<br><hr><br>" + indexTable + "<hr>")
                f.write("\n<script>setTimeout(function(){window.location.reload(1);}, 100*60*" + str(minutesSleep) + " );</script>")
            print("Written to file: ", f.name)

        time.sleep(minutesSleep * 60)
