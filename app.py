import csv
from datetime import datetime
from flask import Flask, render_template, request, flash

from main import get_stock_data, filter_dates, create_chart

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

chart_types = ["Bar", "Line"]

time_series = {
    "Intraday": "TIME_SERIES_INTRADAY",
    "Daily": "TIME_SERIES_DAILY",
    "Weekly": "TIME_SERIES_WEEKLY",
    "Monthly": "TIME_SERIES_MONTHLY"
}

# Function to read the stock symbols from the stocks.csv file
def get_symbols():
    symbols = []

    with open('stocks.csv', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        for row in reader:
            symbols.append(row['Symbol'])

    return sorted(symbols)

# Function to check that a date is in YYYY-MM-DD format
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


# route for the home page. Load page with get or post method
@app.route('/', methods=('GET', 'POST'))
def index():
    symbols = get_symbols()
    chart_html = None

    if request.method == 'POST':
        symbol = request.form['symbol']
        chart_type = request.form['chart_type']
        series = request.form['time_series']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # flash an error message if an input is not valid
        # else get the stock data and make the chart
        if symbol not in symbols:
            flash('Please choose a stock symbol')
        elif chart_type not in chart_types:
            flash('Please choose a chart type')
        elif series not in time_series:
            flash('Please choose a time series')
        elif not is_valid_date(start_date):
            flash('Please enter a valid start date')
        elif not is_valid_date(end_date):
            flash('Please enter a valid end date')
        elif end_date < start_date:
            flash('End date cannot be before the start date')
        else:
            df = get_stock_data(symbol, time_series[series], '60min')

            if df is None:
                flash('Could not get stock data. Check the terminal for the API message')
            else:
                df = filter_dates(df, start_date, end_date)
                chart = create_chart(df, symbol, chart_type, start_date, end_date)

                if chart is None:
                    flash('There is no data for that date range')
                else:
                    # turn the chart into html so it can show on the page
                    chart_html = chart.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template('index.html', symbols=symbols, chart_types=chart_types, time_series=time_series, chart_html=chart_html)

# host 0.0.0.0 is needed so the app can be reached from inside Docker
app.run(host="0.0.0.0", port=5008)