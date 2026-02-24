from flask import Flask, request
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# ===============================
# DASHBOARD PAGE
# ===============================
@app.route("/", methods=["GET"])
def home():
    symbol = request.args.get("symbol", "RELIANCE.NS")

    stock = yf.Ticker(symbol)
    hist = stock.history(period="1mo")

    if hist.empty:
        return "Invalid Stock Symbol"

    price = hist["Close"].iloc[-1]
    yesterday = hist["Close"].iloc[-2]
    change = ((price - yesterday) / yesterday) * 100

    chart_data = hist["Close"].tolist()
    dates = [str(date.date()) for date in hist.index]

    color = "green" if change >= 0 else "red"

    return f"""
    <html>
    <head>
        <title>NSE Pro Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-dark text-light">

    <div class="container mt-5">
        <h1 class="text-center">NSE Pro Dashboard 🔥</h1>

        <div class="text-end">
            <a href="/screener" class="btn btn-warning">Go to Screener 🚀</a>
        </div>

        <form method="GET" class="text-center my-4">
            <input type="text" name="symbol" placeholder="Enter Stock (Example: TCS.NS)" class="form-control w-50 mx-auto" required>
            <button class="btn btn-success mt-2">Search</button>
        </form>

        <h3>{symbol}</h3>
        <h4>₹ {round(price,2)} 
            <span style="color:{color};">({round(change,2)}%)</span>
        </h4>

        <canvas id="stockChart"></canvas>
    </div>

    <script>
        const ctx = document.getElementById('stockChart').getContext('2d');
        const stockChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {dates},
                datasets: [{{
                    label: '{symbol} Price',
                    data: {chart_data},
                    borderColor: '{color}',
                    fill: false
                }}]
            }}
        }});
    </script>

    </body>
    </html>
    """

# ===============================
# SCREENER PAGE (TOP500 + RSI)
# ===============================
@app.route("/screener")
def screener():

    try:
        df = pd.read_csv("top500.csv.txt", header=None)
        stocks = df[0].tolist()
    except:
        return "top500.csv.txt file not found"

    buy_stocks = []

    for symbol in stocks:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="3mo")

            if len(hist) < 50:
                continue

            # Moving Averages
            hist["20DMA"] = hist["Close"].rolling(20).mean()
            hist["50DMA"] = hist["Close"].rolling(50).mean()

            # RSI Calculation
            delta = hist["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss
            hist["RSI"] = 100 - (100 / (1 + rs))

            latest = hist.iloc[-1]

            price = latest["Close"]
            ma20 = latest["20DMA"]
            ma50 = latest["50DMA"]
            rsi = latest["RSI"]

            # Strong Momentum Buy Logic
            if price > ma20 and ma20 > ma50 and 50 < rsi < 70:
                buy_stocks.append({
                    "symbol": symbol,
                    "price": round(price,2),
                    "rsi": round(rsi,2)
                })

        except:
            continue

    html = """
    <html>
    <head>
        <title>Stock Screener</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-dark text-light">
    <div class="container mt-5">
        <h1>🔥 Strong Momentum Buy Signals (Top500)</h1>
        <div class="mb-3">
            <a href="/" class="btn btn-primary">Back to Dashboard</a>
        </div>
        <table class="table table-dark table-striped">
        <tr>
            <th>Stock</th>
            <th>Price</th>
            <th>RSI</th>
        </tr>
    """

    if buy_stocks:
        for stock in buy_stocks:
            html += f"""
            <tr>
                <td>{stock['symbol']}</td>
                <td>₹{stock['price']}</td>
                <td>{stock['rsi']}</td>
            </tr>
            """
    else:
        html += """
        <tr>
            <td colspan="3">No Strong Buy Signals Today</td>
        </tr>
        """

    html += """
        </table>
    </div>
    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    app.run(debug=True)