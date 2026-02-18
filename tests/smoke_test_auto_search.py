#!/usr/bin/env python3
import os
import json
import sys

# Ensure auto-search is enabled for the test
os.environ.setdefault('ENABLE_AUTO_SEARCH', 'true')

query = "What's the latest on quantum computing?"

def auto_search_results(query):
    results = []
    try:
        if os.getenv('ENABLE_AUTO_SEARCH', 'true').lower() in ('1', 'true', 'yes', 'on'):
            import google_search_utils
            raw = google_search_utils.google_search(query, num_results=3) or []
            # Normalize
            for item in raw:
                item['title'] = item.get('title', '')
                item['snippet'] = item.get('snippet', '')
                link = item.get('link') or item.get('url') or item.get('href') or ''
                item['link'] = link
            results = raw
            if results:
                print(f"Auto-search found {len(results)} result(s) for query: {query}")
    except Exception as e:
        print(f"Auto-search failed: {e}", file=sys.stderr)
        results = []
    return results

search_results = auto_search_results(query)

# Build time context
local_time_string = '2025-08-23 12:34:00'
time_zone = 'UTC'
time_zone_offset = '0'

time_context = (
    f"Current user local time: {local_time_string} (timezone: {time_zone}, offset: {time_zone_offset} min). "
    "If the user asks for the current time, date, or anything time-related, use this as the present moment."
)

prompt_parts = [time_context]

if search_results:
    summary_lines = []
    for idx, item in enumerate(search_results[:3]):
        title = item.get('title', '')
        snippet = item.get('snippet', '')
        link = item.get('link', '')
        summary_lines.append(f"{idx + 1}. {title} - {snippet} (URL: {link})")
    summary = "\n".join(summary_lines)
    prompt_parts.append("Top search results:\n" + summary)

prompt_parts.append(f"User Query: {query}")
final_prompt = "\n\n".join(prompt_parts)

print("\nFINAL PROMPT:\n")
print(final_prompt)

search_results_payload = [
    {'title': r.get('title', ''), 'snippet': r.get('snippet', ''), 'link': r.get('link', '')}
    for r in search_results[:3]
]

print("\nSEARCH RESULTS PAYLOAD:\n")
print(json.dumps(search_results_payload, indent=2))
