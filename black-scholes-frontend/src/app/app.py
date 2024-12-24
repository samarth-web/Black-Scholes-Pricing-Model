from flask import Flask, render_template, request, redirect,url_for
import yfinance as yf
import numpy as np
from scipy.stats import norm
import datetime
import io
import matplotlib.pyplot as plt
from textblob import TextBlob
from newsapi import NewsApiClient

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def start():
    result = None
    if request.method == 'POST':
        try:
            value = request.form.get('choice')
            if value == 'Calculator':
                result = 1
                return redirect(url_for('calculator'))
            else:
                result = 2
                return redirect(url_for('real_data'))

        except Exception as e:
              result = ("Error: ", e)   
   
    return render_template('start.html', result=result)

@app.route('/real_data', methods=["GET","POST"])
def real_data():
    result = None
        
    if request.method == 'POST':
        try:
            symbol = request.form.get('ticker')
            stock = yf.Ticker(symbol)
            stock_price = stock.history(period="1d")["Close"].iloc[-1]
            name = stock.info.get("longName", "Company name not found")
            expiring_dates = stock.options
            early_date = expiring_dates[0] #Getting the first expiring date
            options_chain = stock.option_chain(early_date)
            calls = options_chain.calls
            puts = options_chain.puts
            strike_price_calls = calls['strike'].iloc[0]
            strike_price_puts = puts['strike'].iloc[0]
            today = datetime.date.today()
            early_date_obj = datetime.datetime.strptime(early_date, '%Y-%m-%d').date()
            time_to_expiry = (early_date_obj - today).days / 365
            implied_volatility_calls = calls[calls['strike'] == strike_price_calls]['impliedVolatility'].values[0]
            implied_volatility_puts = puts[puts['strike'] == strike_price_puts]['impliedVolatility'].values[0]
            treasury_data = yf.Ticker("^IRX")
            latest_data = treasury_data.history(period="1d")
            treasury_yield = latest_data['Close'].iloc[-1]
            risk_free_rate = treasury_yield/100 
            option_premium_call = calls[calls['strike'] == strike_price_calls]['lastPrice']
            option_premium_puts = puts[puts['strike'] == strike_price_puts]['lastPrice']
            
            S = stock_price
            K = strike_price_calls
            r = risk_free_rate
            T = time_to_expiry
            sigma = implied_volatility_calls
            option_type = "call"
          
            price = black_scholes_price(S, K, r, T, sigma, option_type)
            greeks = black_scholes_greeks(S, K, r, T, sigma, option_type)

          

            val = 0
            sum = 0
            count = 0
            newsapi = NewsApiClient(api_key='d09f2385c542494988c905a29e19a0f5')
            articles = newsapi.get_everything(q=ticker, language='en', page_size=50, sort_by='relevancy')
            headlines = [article['title'] for article in articles['articles']]
            for headline in headlines: 
                val = 0
                val = Textblob(headline).sentiment.polarity
                val = val + 1
                val = val/2
                sum+ = val
                count = count + 1
            headline_score = sum/count



          
            
  
            
            result = {"name": name, "stock price": stock_price, "time to maturity": time_to_expiry, "implied volatility": implied_volatility_calls, "risk free rate": risk_free_rate, "call strike price": strike_price_calls
            , "price": price, "Real-world premium": option_premium_call.values[0]
            }

        except Exception as e:
              result = ("Error: ", e)
       

    return render_template('findata.html', result=result)

   

@app.route('/calculator', methods=["GET","POST"])
def calculator():
    result = None
    if request.method == 'POST':
        try:

            app.logger.info(request.form)
            S = float(request.form.get('S'))
            K = float(request.form.get('K'))
            r = float(request.form.get('r'))
            T = float(request.form.get('T'))
            sigma = float(request.form.get('sigma'))
            option_type = request.form.get('option_type', 'call').strip().lower()
             
            if option_type == 'call':
                pass
            elif option_type == 'put':
                pass
            else:
                raise ValueError("Option type must be 'call' or 'put'.")

            price = black_scholes_price(S, K, r, T, sigma, option_type)
            greeks = black_scholes_greeks(S, K, r, T, sigma, option_type)

            result =("Price: ", price ,", Greeks: ", greeks)
            
        except Exception as e:
                result = ("Error: ", e)
   
    return render_template('app.html', result=result)


def d1_d2(S, K, r, T, sigma):
   
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2

def black_scholes_price(S, K, r, T, sigma, option_type):
  
    d1, d2 = d1_d2(S, K, r, T, sigma)
    
    if option_type.lower() == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    elif option_type.lower() == 'put':
        price = K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'.")

    return price

def black_scholes_greeks(S, K, r, T, sigma, option_type):
   
    d1, d2 = d1_d2(S, K, r, T, sigma)
    pdf_d1 = norm.pdf(d1)  
    
    
    discount = np.exp(-r * T)

   
    if option_type.lower() == 'call':
        delta = norm.cdf(d1)
    else:
        delta = norm.cdf(d1) - 1

    gamma = pdf_d1 / (S * sigma * np.sqrt(T))


    vega = S * pdf_d1 * np.sqrt(T)

    if option_type.lower() == 'call':
        theta = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(T))) \
                - r * K * discount * norm.cdf(d2)
    else:
        theta = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(T))) \
                + r * K * discount * norm.cdf(-d2)

   
    if option_type.lower() == 'call':
        rho = K * T * discount * norm.cdf(d2)
    else:
        rho = -K * T * discount * norm.cdf(-d2)

    greeks = {
        'Delta': delta,
        'Gamma': gamma,
        'Vega': vega,
        'Theta': theta,
        'Rho': rho
    }

    return greeks

        
   
 

if __name__ == '__main__':
    app.run(debug=True)

