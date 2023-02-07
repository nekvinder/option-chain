import os
import ray
import json
import time
from tabulate import tabulate
import datetime
import urllib.parse
from helper import getJson, printProgressBar

isEnvTest = os.environ.get("ENV") == "test"
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
    return resSortedOnOI[0][0]


def getData(sym, isIndex=False):
    result = {"sym": sym}

    searchRecordsCount = 5
    url = indicesUrl + sym if isIndex else equitiesUrl + sym
    json_obj = getJson(url, cookies=cookies)
    underlying_value = json_obj["records"]["underlyingValue"]

    # put
    splitIndex = 0
    for i in range(len(json_obj["filtered"]["data"])):
        if json_obj["filtered"]["data"][i]["strikePrice"] > underlying_value:
            splitIndex = i
            break

    result["put"] = getOIAnalysis(json_obj, splitIndex, searchRecordsCount, "PE")
    result["call"] = getOIAnalysis(json_obj, splitIndex, searchRecordsCount, "CE")

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


@ray.remote
def getStocksData(stockList, prefix, isIndex=False):
    res = []
    for stock in stockList:
        printProgressBar(stockList.index(stock) + 1, len(stockList), prefix=prefix, suffix="Complete", length=50)
        try:
            res.append(getData(urllib.parse.quote(stock), isIndex=isIndex))
        except Exception as e:
            print("Error for", stock, e)
    return res


def getAnalysis(isIndex=True):
    if isIndex:
        stockList = ["NIFTY", "BANKNIFTY"]
    else:
        stockList = getStockList()
        if isEnvTest:
            stockList = stockList[:15]

    prefix = "Progress: Index" if isIndex else "Progress: Equity"
    printProgressBar(0, len(stockList), prefix=prefix, suffix="Complete", length=50)

    ret_id1 = getStocksData.remote(stockList[len(stockList) // 2 :], prefix, isIndex=isIndex)
    ret_id2 = getStocksData.remote(stockList[: len(stockList) // 2], prefix, isIndex=isIndex)
    ret1, ret2 = ray.get([ret_id1, ret_id2])

    res = ret1 + ret2
    # sort res based on analysisValue
    res = [i for i in res if i is not None]
    res = sorted(res, key=lambda x: x["analysisValue"])

    countResCall = len([i for i in res if i["analysisType"] == "call"])
    countResPut = len([i for i in res if i["analysisType"] == "put"])

    linkRef = f"https://in.tradingview.com/chart/?symbol=NSE%3A"

    tableHeader = ["Stock", "Put OI", "Current", "Call OI", "Analysis", "Analysis Value", "Link"]
    tableData = []
    for r in res:
        tableData.append([r["sym"], r["put"], r["currentValue"], r["call"], r["analysisType"], r["analysisValue"], f'<a target="_" href="{linkRef + r["sym"]}">Chart</a>'])

    htmlTable = tabulate(tableData, headers=tableHeader, tablefmt="unsafehtml")
    htmlStr = ""
    if not isIndex:
        htmlStr += f"<center><h4>Total - Call({countResCall}) Put({countResPut})</h4></center>"
    htmlStr += "<center>" + htmlTable + "</center>"
    return htmlStr


if __name__ == "__main__":
    while True:
        table = getAnalysis()
        minutesSleep = 15
        indexTable = getAnalysis(isIndex=False)
        currentTime = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        for filename in [currentTime + ".html", "latest.html"]:
            with open(filename, "w") as f:
                f.write(f"<center><h4>Last Update At: {datetime.datetime.now().strftime('%Y %m %d - %H:%M:%S')}</h4></center>")
                f.write(table + "\n<br><hr><br>" + indexTable + "<hr>")
                f.write("\n<script>setTimeout(function(){window.location.reload(1);}, 100*60*" + str(1) + " );</script>")
            print("Written to file: ", f.name)
        exit(0)
        time.sleep(minutesSleep * 60)
