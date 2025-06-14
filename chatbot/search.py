# chatbot/search.py
import os
from serpapi import GoogleSearch

def search_web(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERP_API_KEY")
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return [res['link'] for res in results.get("organic_results", [])[:3]]
