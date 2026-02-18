import os
import requests

GOOGLE_API_KEY = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')


def google_search(query, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': num_results
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get('items', [])


def analyze_results(results, keywords=None, min_snippet_length=80):
    relevant = []
    for item in results:
        snippet = item.get('snippet', '')
        if len(snippet) >= min_snippet_length:
            if not keywords or any(kw.lower() in snippet.lower() for kw in keywords):
                relevant.append(item)
    return relevant


def extract_keywords(results, top_n=5):
    # Simple keyword extraction: split snippets into words, count frequency
    from collections import Counter
    words = []
    for item in results:
        words += item.get('snippet', '').split()
    common = Counter(words).most_common(top_n)
    return [w for w, _ in common]


def multi_step_search(query):
    # Step 1: Initial search
    results = google_search(query)
    relevant = analyze_results(results)
    if relevant:
        return relevant[0]['snippet']
    # Step 2: Refine query
    keywords = extract_keywords(results)
    refined_query = query + ' ' + ' '.join(keywords)
    results2 = google_search(refined_query)
    relevant2 = analyze_results(results2, keywords)
    if relevant2:
        return relevant2[0]['snippet']
    # Fallback: return first snippet if nothing else
    if results2:
        return results2[0].get('snippet', 'No relevant results found.')
    return 'No relevant results found.'
