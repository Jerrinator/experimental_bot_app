#!/usr/bin/env python3
import os
import json
from datetime import datetime

query = "What's the latest on quantum computing?"

# Simulated search results (3 items)
search_results = [
    {
        'title': 'Quantum Supremacy Achieved in New Experiment',
        'snippet': 'Researchers report a milestone demonstrating quantum advantage in specific tasks.',
        'link': 'https://example.com/quantum-supremacy'
    },
    {
        'title': 'Advances in Quantum Error Correction',
        'snippet': 'New error-correction codes improve coherence times and scalability.',
        'link': 'https://example.com/quantum-error-correction'
    },
    {
        'title': 'Commercial Quantum Computers Progress',
        'snippet': 'Companies announce roadmap and new hardware with increased qubits.',
        'link': 'https://example.com/commercial-quantum'
    }
]

# Build time context
local_time_string = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
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
