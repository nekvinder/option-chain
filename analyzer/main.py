import os
import json
import time
from tabulate import tabulate
import datetime
import urllib.parse
from helper import getJson, printProgressBar, sendEmail, insertIntoTable, getCallPutHistoryToday

scriptTriggerTime = datetime.datetime.now()
isEnvTest = os.environ.get("ENV") == "test"
isDebug = os.environ.get("DEBUG") == "true"
indicesUrl = "https://www.nseindia.com/api/option-chain-indices?symbol="
equitiesUrl = "https://www.nseindia.com/api/option-chain-equities?symbol="

cookies = None


def getStockList():
    try:
        return getJson("https://www.nseindia.com/api/master-quote", cookies)["data"]
    except:
        print("Error in getting stock list, using local list")
        stocksStr = '["AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS", "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT", "ASTRAL", "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE", "BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT", "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BOSCHLTD", "BPCL", "BRITANNIA", "BSOFT", "CANBK", "CANFINHOME", "CHAMBLFERT", "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE", "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", "CUB", "CUMMINSIND", "DABUR", "DALBHARAT", "DEEPAKNTR", "DELTACORP", "DIVISLAB", "DIXON", "DLF", "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND", "FEDERALBNK", "FSL", "GAIL", "GLENMARK", "GMRINFRA", "GNFC", "GODREJCP", "GODREJPROP", "GRANULES", "GRASIM", "GUJGASLTD", "HAL", "HAVELLS", "HCLTECH", "HDFC", "HDFCAMC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDCOPPER", "HINDPETRO", "HINDUNILVR", "HONAUT", "IBULHSGFIN", "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDEA", "IDFC", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIACEM", "INDIAMART", "INDIGO", "INDUSINDBK", "INDUSTOWER", "INFY", "INTELLECT", "IOC", "IPCALAB", "IRCTC", "ITC", "JINDALSTEL", "JKCEMENT", "JSWSTEEL", "JUBLFOOD", "KOTAKBANK", "L&TFH", "LALPATHLAB", "LAURUSLABS", "LICHSGFIN", "LT", "LTIM", "LTTS", "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MCDOWELL-N", "MCX", "METROPOLIS", "MFSL", "MGL", "MOTHERSON", "MPHASIS", "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI", "NAVINFLUOR", "NESTLEIND", "NMDC", "NTPC", "OBEROIRLTY", "OFSS", "ONGC", "PAGEIND", "PEL", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", "PIIND", "PNB", "POLYCAB", "POWERGRID", "PVR", "RAIN", "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD", "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SRF", "SRTRANSFIN", "SUNPHARMA", "SUNTV", "SYNGENE", "TATACHEM", "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TORNTPOWER", "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WHIRLPOOL", "WIPRO", "ZEEL", "ZYDUSLIFE"]'
        return json.loads(stocksStr)


def getOIAnalysis(json_obj, splitIndex, searchRecordsCount, callType):
    res = []
    start = splitIndex - searchRecordsCount if callType == "CE" else splitIndex
    end = splitIndex if callType == "CE" else splitIndex + searchRecordsCount
    for i in range(start, end):
        openInterest = json_obj["filtered"]["data"][i][callType]["openInterest"]
        strikePrice = json_obj["filtered"]["data"][i]["strikePrice"]
        res.append((strikePrice, openInterest))
    resSortedOnOI = sorted(res, key=lambda x: x[1], reverse=True)
    if isDebug:
        print(resSortedOnOI)
    return resSortedOnOI[0][0]


def getOISum(json_obj, splitIndex, searchRecordsCount, callType):
    res = []
    start = splitIndex - searchRecordsCount
    end = splitIndex + searchRecordsCount
    for i in range(start, end):
        openInterest = json_obj["filtered"]["data"][i][callType]["openInterest"]
        strikePrice = json_obj["filtered"]["data"][i]["strikePrice"]
        res.append((strikePrice, openInterest))
    resSortedOnOI = sorted(res, key=lambda x: x[1], reverse=True)
    if isDebug:
        print(resSortedOnOI)
    return resSortedOnOI[0][0]


def getData(sym, isIndex=False):
    if isDebug:
        print(sym)
    result = {"sym": sym}

    searchRecordsCount = 5
    url = indicesUrl + sym if isIndex else equitiesUrl + sym
    json_obj = getJson(url, cookies=cookies)

    underlying_value = json_obj["records"]["underlyingValue"]
    splitIndex = 0
    for i in range(len(json_obj["filtered"]["data"])):
        if json_obj["filtered"]["data"][i]["strikePrice"] > underlying_value:
            splitIndex = i
            break

    intrestedRecordsRange = 5
    start = splitIndex - intrestedRecordsRange + 1
    end = splitIndex + intrestedRecordsRange + 1
    result["recordsInRange"] = json_obj["filtered"]["data"][start:end]
    result["ceSum"] = 0
    result["peSum"] = 0
    result["isGreaterThan999"] = False
    for i in range(len(result["recordsInRange"])):
        # print("ce", result["recordsInRange"][i]["CE"]["openInterest"])
        # print("pe", result["recordsInRange"][i]["PE"]["openInterest"])
        peValue = int(result["recordsInRange"][i]["PE"]["openInterest"])
        ceValue = int(result["recordsInRange"][i]["CE"]["openInterest"])

        result["ceSum"] += ceValue
        result["peSum"] += peValue
        if peValue > 999 or ceValue > 999:
            result["isGreaterThan999"] = True

    result["pcr"] = result["peSum"] / result["ceSum"]
    # print(result["pcr"])

    # result["put"] = getOIAnalysis(json_obj, splitIndex, searchRecordsCount, "CE")
    # result["call"] = getOIAnalysis(json_obj, splitIndex, searchRecordsCount, "PE")

    # result["currentValue"] = underlying_value
    # putDiff = result["put"] - underlying_value
    # callDiff = result["call"] - underlying_value

    # if abs(putDiff) < abs(callDiff):
    #     result["analysisType"] = "put"
    #     result["analysisValue"] = round(abs(putDiff), 3)
    # else:
    #     result["analysisType"] = "call"
    #     result["analysisValue"] = round(abs(callDiff), 3)

    return result


def getAnalysis(isIndex=True):

    if isIndex:
        stockList = ["NIFTY", "BANKNIFTY"]
        stockListSuffixGF = ["NIFTY_50", "NIFTY_BANK"]
    else:
        stockList = getStockList()
        if isEnvTest:
            pass
            # stockList = stockList[:5]

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
    res = [i for i in res if i is not None and i["isGreaterThan999"]]
    res = sorted(res, key=lambda x: x["pcr"])

    # countResCall = len([i for i in res if i["analysisType"] == "call"])
    # countResPut = len([i for i in res if i["analysisType"] == "put"])

    linkRefTD = f"https://in.tradingview.com/chart/?symbol=NSE%3A"
    linkRefGF = f"https://www.google.com/finance/quote/"
    gfSuffix = "INDEXNSE" if isIndex else "NSE"

    # tableHeader = ["Stock", "Put OI", "Current", "Call OI", "Analysis", "Analysis Value", "Link TD", "Link GF"]
    tableHeader = ["Stock", "PCR", "TV", "GF"]
    tableData = []
    for r in res:
        symGF = stockListSuffixGF[stockList.index(r["sym"])] if isIndex else r["sym"]
        tableData.append(
            [
                r["sym"],
                round(r["pcr"], 2),
                # r["currentValue"],
                # r["call"],
                # r["analysisType"],
                # r["analysisValue"],
                f'<a target="_" href="{linkRefTD + r["sym"]}">Chart</a>',
                f'<a target="_" href="{linkRefGF + symGF + ":" + gfSuffix }">GF</a>',
            ],
        )

    htmlStr = ""
    htmlTable = tabulate(tableData, headers=tableHeader, tablefmt="unsafehtml")
    if not isIndex:
        countCall = len([i for i in res if i["pcr"] > 1])
        countPut = len([i for i in res if i["pcr"] < 1])
        insertIntoTable(scriptTriggerTime, countCall, countPut)
        htmlStr += f"<center><h4>Total - Call({countCall}) Put({countPut})</h4></center>"
    htmlStr += "<center>" + htmlTable + "</center>"
    return htmlStr


def getCallPutHistoryTable():
    tableHeader = ["Time", "Call", "Put"]
    tableData = []
    histData = getCallPutHistoryToday()

    for i in range(len(histData)):
        callColumnIndex = 3
        row = histData[i]
        prevRow = histData[i - 1] if i > 0 else row
        isUp = row[callColumnIndex] > prevRow[callColumnIndex]
        isDown = row[callColumnIndex] < prevRow[callColumnIndex]
        symbol = "▲" if isUp else "▼" if isDown else "▬"
        tableData.append(
            [datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f").strftime("%H:%M"), row[3], row[4], symbol],
        )
    htmlTable = tabulate(tableData, headers=tableHeader, tablefmt="unsafehtml")
    return "<center>" + htmlTable + "</center>"


def generateLocalFiles():
    # while True:
    table = getAnalysis()
    # minutesSleep = 15
    indexTable = getAnalysis(isIndex=False)
    scriptTriggerTimeStr = f"{scriptTriggerTime.strftime('%Y%m%d%H%M%S')}"
    for filename in [scriptTriggerTimeStr + ".html", "latest.html"]:
        with open(filename, "w") as f:
            f.write(f"<center><h4>Last Update At: {scriptTriggerTime.strftime('%Y %m %d - %H:%M:%S')}</h4></center>")
            f.write(table + "\n<br><hr><br>" + indexTable + "<hr>")
            # f.write("\n<script>setTimeout(function(){window.location.reload(1);}, 100*60*" + str(1) + " );</script>")
        print("Written to file: ", f.name)
    # time.sleep(minutesSleep * 60)


if __name__ == "__main__":
    # while True:
    table = getAnalysis()
    # minutesSleep = 15
    indexTable = getAnalysis(isIndex=False)
    finalEmailStr = """<style>
  * {
    font-family: monospace, sans-serif;
  }

  td {
    padding-left: 20px;
  }
</style>"""

    currentTime = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    finalEmailStr += f"<center><h4>Last Update At: {datetime.datetime.now().strftime('%Y %m %d - %H:%M:%S')}</h4></center>"
    finalEmailStr += table + "\n<br><hr><br>" + getCallPutHistoryTable() + "<br><hr><br>" + indexTable + "<hr>"
    if isEnvTest:
        for filename in [currentTime + ".html", "latest.html"]:
            with open(filename, "w") as f:
                f.write(finalEmailStr)
                f.write("\n<script>setTimeout(function(){window.location.reload(1);}, 100*60*" + str(1) + " );</script>")
            print("Written to file: ", f.name)
        pass
    else:
        sendEmail(finalEmailStr)
    # time.sleep(minutesSleep * 60)
