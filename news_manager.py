import requests

# Country code mapping
country_code_mapping = {
    "united states": "us",
    "canada": "ca",
    "united kingdom": "gb",
    "australia": "au",
    "india": "in",
    "germany": "de",
    "france": "fr",
    "italy": "it",
    "spain": "es",
    "brazil": "br",
    # Add more countries as needed
}

def get_news(api_key, country, query=None):
    """Fetch the latest news using the News API for a specific country or related to a specific query."""
    if query:
        # If a query is provided, use it to search for related news
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"
    else:
        # Otherwise, fetch news for the specified country
        url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={api_key}"
    
    response = requests.get(url)
    
    # Debugging: Print the response status code
    print(f"Response Status Code: {response.status_code}")
    
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        news_list = []
        for article in articles[:5]:  # Get top 5 news articles
            title = article.get('title')
            news_list.append(title)
        return news_list
    else:
        # Debugging: Print the error message
        print(f"Error fetching news: {response.json()}")
        return None 