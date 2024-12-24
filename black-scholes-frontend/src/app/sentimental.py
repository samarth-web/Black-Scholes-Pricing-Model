from textblob import TextBlob
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import tweepy
import requests



twitter_bearer_token = "AAAAAAAAAAAAAAAAAAAAADbSxgEAAAAA4K%2B1oKo0ftzRlHbmwLVJ7ebt74U%3Deq9v7fgIu9q70B4iqPPdBagEXrD3YAkVnl6k4TZ0tbZaXEwsHY"

alpha_API_KEY = 'EMQEQKTXOU39TG1I.'
BASE_URL = 'https://www.alphavantage.co/query'
params = {
    'function': 'NEWS_SENTIMENT',
    'tickers': 'AAPL',
    'apikey': alpha_API_KEY
}

response = requests.get(BASE_URL, params=params)
data = response.json()

sentiment_scores = [article['overall_sentiment_score'] for article in data.get('feed', [])]

for score in sentiment_scores:
    print(type(score))

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

val = 0

count = 0

newsapi = NewsApiClient(api_key='d09f2385c542494988c905a29e19a0f5')
today = datetime.now().strftime('%Y-%m-%d')
one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
articles = newsapi.get_everything(q='Bangladesh', language='en', from_param=one_week_ago, to=today, page_size=100, sort_by='relevancy')
headlines = [article['title'] for article in articles['articles']]

threshold = 0.1  # Define neutrality range
sentiment_scores = []

for headline in headlines:
    sentiment = TextBlob(headline).sentiment.polarity
    if abs(sentiment) > threshold:  
        normalized_sentiment = (sentiment + 1) / 2  
        sentiment_scores.append(normalized_sentiment)

print((sum(sentiment_scores) / len(sentiment_scores)) * 100)
