from flask import Flask, render_template, request, redirect,url_for
import yfinance as yf
import numpy as np
from scipy.stats import norm
import io
import matplotlib.pyplot as plt
from textblob import TextBlob
from newsapi import NewsApiClient
from textblob import TextBlob
from newsapi import NewsApiClient
from datetime import timedelta, datetime
import tweepy
import requests
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline

def sentiment_analysis(symbol):

    try:
        twitter_bearer_token = "AAAAAAAAAAAAAAAAAAAAADbSxgEAAAAA4K%2B1oKo0ftzRlHbmwLVJ7ebt74U%3Deq9v7fgIu9q70B4iqPPdBagEXrD3YAkVnl6k4TZ0tbZaXEwsHY"

        alpha_API_KEY = 'EMQEQKTXOU39TG1I.'
        BASE_URL = 'https://www.alphavantage.co/query'
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'apikey': alpha_API_KEY,
            'limit': 1000
        }
        
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        agg = 0
        counting = 0
        sentiment_scores = [article['overall_sentiment_score'] for article in data.get('feed', [])]
        for score in sentiment_scores:
            score = (score+1)/2
            agg = agg + score
            counting = counting + 1
        if counting == 0:
            value = 0.5
        else:
            value = agg/counting
        print("VALUE:" ,value)
  
        feed = data.get('feed', [])
        if not feed:
            print("No articles found in the response.")
            print("API Response:", data)
         



        #Free Twitter(X) API usage allowed is only 100 posts per month (use cautiously)


        # client = tweepy.Client(bearer_token=twitter_bearer_token)
        # query_term = "AAPL"
        # language_filter = "lang:en"
        # query = f"{query_term} {language_filter}"

        # tweets = client.search_recent_tweets(query=query, max_results=10, tweet_fields=["text", "created_at", "lang"])
        # print(tweets)
        # val = 0
        # sum = 0
        # count = 0

        # for tweet in tweets:
        #     val = TextBlob(tweet).sentiment.polarity
        #     val = val + 1
        #     val = val / 2
        #     sum += val
        #     count += 1

        # if count > 0:
        #     tweet_score = sum / count
        #     print(tweet_score)

        val1 = 0

        count1 = 0

        newsapi = NewsApiClient(api_key='d09f2385c542494988c905a29e19a0f5')
        today = datetime.now().strftime('%Y-%m-%d')
        one_week_ago = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        articles = newsapi.get_everything(
            q=symbol,
            language='en',
            from_param=  one_week_ago,
            to= today,
            page_size=100,
            sort_by='relevancy'
        )
        titles = [article.get('title', '') for article in articles['articles']]

        headlines = []
        for article in articles['articles']:
            combined_text = (article.get('title') or '') + ' ' + (article.get('description') or '')
            headlines.append(combined_text)

        clean = re.compile('<.*?>')
        headlines = [re.sub(clean, '', h) for h in headlines]  #removing HTML tags
        headlines = [re.sub(r'http\S+|www\S+', '', h) for h in headlines]

        threshold = 0.1  # Define neutrality range
        sentiment_scores = []

        analyzer = SentimentIntensityAnalyzer()
        for headline in headlines:
            scores = analyzer.polarity_scores(headline)
            compound = scores['compound']
            if abs(compound) > threshold:  
                normalized_sentiment = (compound + 1) / 2  
                sentiment_scores.append(normalized_sentiment)
        if len(sentiment_scores) == 0:
            res = 0.5
        else:
            res = (sum(sentiment_scores) / len(sentiment_scores)) 
        print("RES", res)
       # print("val", val)
        var = "trial123"
       
        fin_val = 0
        stock = yf.Ticker(symbol)
        yahoo_news = stock.news
       
       
       
        finbert = pipeline("text-classification", model="ProsusAI/finbert")
        print("Number of articles:", len(yahoo_news))

        sentiment_scores = []
        for headline in headlines:
            title = headline
            if title:
                sentiment = finbert(title)
                score = sentiment[0]['score']
                label = sentiment[0]['label']
                normalized_score = score if label == 'positive' else (1 - score if label == 'negative' else 0.5)
                sentiment_scores.append(normalized_score)

        
        if sentiment_scores:
            overall_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            fin_val = overall_sentiment
        else:
            fin_val = 0.5  # Neutral sentiment as fallback

        print(fin_val)
        if value == 0.5:
            total = (0.6*res)+(0.4*value)
        else:
            total = (0.2*res + 0.6*value + 0.2*fin_val)
        print("total: ",total) 
    
    except Exception as e:
              total = 0
              result = ("Error: in sentimental analysis", e)
              print(yf.Ticker(symbol).news)
              print(result)
    

      
    return total


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
            today = datetime.today().date()
            early_date_obj = datetime.strptime(early_date, '%Y-%m-%d').date()
            time_to_expiry = (early_date_obj - today).days / 365
            if time_to_expiry <= 0:
                print("Expiration date is today or has already passed. Adjusting T to 1 day.")
            time_to_expiry = 1 / 365
            implied_volatility_calls = calls[calls['strike'] == strike_price_calls]['impliedVolatility'].values[0]
            implied_volatility_puts = puts[puts['strike'] == strike_price_puts]['impliedVolatility'].values[0]
            treasury_data = yf.Ticker("^IRX")
            latest_data = treasury_data.history(period="1d")
            treasury_yield = latest_data['Close'].iloc[-1]
            risk_free_rate = treasury_yield/100 
            option_premium_call = calls[calls['strike'] == strike_price_calls]['lastPrice']
            option_premium_puts = puts[puts['strike'] == strike_price_puts]['lastPrice']
            optimized_implied_volatility = sentiment_analysis(symbol)
            print("hi", sentiment_analysis(symbol))
            print("Today:", today)
            print("Early Date Object:", early_date_obj)
            print("Difference (days):", (early_date_obj - today).days)
            option_type_put = "put"
            

            

            new_volitlity_calls = implied_volatility_calls * (1+2 * (optimized_implied_volatility - 0.5))
            S = stock_price
            K_calls = strike_price_calls
            K_puts = strike_price_puts
            r = risk_free_rate
            T = time_to_expiry
            if T == 0: #Time will go to 0 on weekends so made this temp fix :)
                T = 1
            if K == 0:
                print("this is K", K)
            
            sigma = implied_volatility_calls
            option_type = "call"
            if sigma == 0:
                print("this is sigma" , sigma)
           
            price = black_scholes_price(S, K_calls, r, T, sigma, option_type)
            greeks = black_scholes_greeks(S, K_calls, r, T, sigma, option_type)
            optimized_price = black_scholes_price(S, K_calls, r, T, new_volitlity_calls, option_type)
            put_price = black_scholes_price(S, K_puts, r, T, sigma, option_type_put)
            greeks_put = black_scholes_greeks(S, K_puts, r, T, sigma, option_type_put)
            optimized_price_put = black_scholes_price(S, K_puts, r, T, new_volitlity_calls, option_type_put)

          

                     
            
  
            
            result = {"name": name, "stock price": stock_price, "time to maturity": time_to_expiry, "implied volatility": implied_volatility_calls, "risk free rate": risk_free_rate, "call strike price": strike_price_calls
            , "price": price, "Real-world premium": option_premium_call.values[0], "Optimized premium": optimized_price
            }

        except Exception as e:
              result = ("Error: ", e)
              print(result)
       

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

