import os
import requests
import pandas as pd
import plotly.express as px

API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "")
BASE_URL = "https://www.alphavantage.co/query"

def get_stock_data(symbol, function, interval=None):

    parameters = {
        "function": function,
        "symbol": symbol,
        "outputsize": "full",
        "apikey": API_KEY
    }

    if function == "TIME_SERIES_INTRADAY":
        parameters["interval"] = interval

    try:
        response = requests.get(
            url=BASE_URL,
            params=parameters,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

    except requests.RequestException as error:
        print("Error connecting to Alpha Vantage:", error)
        return None

    if "Error Message" in data:
        print("API Error:", data["Error Message"])
        return None
    
    if "Note" in data:
        print("API limit message:", data["Note"])
        return None

    if "Information" in data:
        print("API Information", data["Information"])
        return None

    time_series_key = next(
        (key for key in data if "Time Series" in key),
        None
    )

    if time_series_key is None:
        print("No stock data was returned.")
        return None

    df = pd.DataFrame.from_dict(
        data[time_series_key],
        orient="index"
    )

    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    df.columns = [
        column.split(". ", 1)[-1].lower()
        for column in df.columns
    ]

    for column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df

def filter_dates(df, start_date, end_date):
    mask = (df.index >= start_date) & (df.index <= end_date)
    return df.loc[mask]

def create_chart(df, symbol, chart_type, start_date, end_date):
    if df.empty:
        print("No stock data available to create a chart.")
        return None

    if "close" not in df.columns:
        print("No closing prices found.")
        return None

    title = f"{symbol} Stock Prices ({start_date} to {end_date})"

    if chart_type == "Bar":
        chart = px.bar(df, x=df.index, y="close", title=title)
    elif chart_type == "Line":
        chart = px.line(df, x=df.index, y="close", title=title)
    else:
        print("Invalid chart type.")
        return None

    chart.update_layout(
        xaxis_title="Date",
        yaxis_title="Closing Price ($)"
    )

    return chart