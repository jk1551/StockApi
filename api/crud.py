import yfinance as yf

symbols = [
    "AAPL",
    "MSFT",
    "AMZN",
    "NVDA",
    "GOOGL",
    "GOOG",
    "META",
    "TSLA"
]


async def get_stock_data():
    # Replace with desired stock symbols
    stocks = []

    for symbol in symbols:
        stock = yf.Ticker(symbol)
        stock_info = stock.info

        stock_data = {
            "symbol": symbol,
            "name": stock_info.get("longName", symbol),
            "price": stock_info.get("currentPrice", 0.0),
        }
        stocks.append(stock_data)

    return stocks


async def get_single_stock(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        stock_data = {
            "symbol": ticker,
            "name": stock_info.get("longName", ticker),
            "price": stock_info.get("currentPrice", 0.0),
        }
        return stock_data;
    except:
        return "No stock was found for this ticker"
