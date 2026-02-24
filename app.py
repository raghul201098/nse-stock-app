from flask import Flask, redirect
import os

app = Flask(__name__)

# 🔹 Root route
@app.route("/")
def home():
    return redirect("/screener")


# 🔹 Screener route
@app.route("/screener")
def screener():
    try:
        with open("top500.csv.txt", "r", encoding="utf-8") as file:
            content = file.read()
    except Exception as e:
        content = f"Error loading file: {e}"

    return f"""
    <html>
    <head>
        <title>NSE Stock Screener</title>
        <style>
            body {{
                font-family: Arial;
                padding: 20px;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <h2>NSE Stock Data</h2>
        <pre>{content}</pre>
    </body>
    </html>
    """


# 🔹 Render PORT binding (VERY IMPORTANT)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
