import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import FlaskChatbotApp

class DummyResponse:
    def __init__(self):
        class Choice:
            def __init__(self):
                class Message:
                    content = ''
                self.message = Message()
        self.choices = [Choice()]
    def to_dict(self):
        return {'choices':[{'message':{'content':''}}]}

class DummyClient:
    def __init__(self):
        pass
    def chat(self):
        return self
    def completions(self):
        return self
    def create(self, **kwargs):
        return DummyResponse()


def run_mock():
    app = FlaskChatbotApp()
    # Inject dummy openai client
    app.openai_client = DummyClient()

    # Simulate a message payload
    data = {
        'message': "let's talk about a ship in a bottle",
        'sessionId': 'test-session',
        'userId': 'test-user',
        'username': 'tester',
        'localTimeString': '8/23/2025, 8:32:08 PM',
        'timeZone': 'America/Chicago',
        'timeZoneOffset': 300
    }

    # Call handler directly
    handler = app.setup_socket_handlers.__wrapped__.__get__(app, FlaskChatbotApp) if hasattr(app.setup_socket_handlers, '__wrapped__') else None
    # Instead of binding to socket, directly call the internal handle_message by constructing expected environment
    # We'll reuse the actual method by calling app.socketio.server.enter_room etc is complex; instead, call the function body via direct method call
    # For now, simply call the auto-search helper and simulate the fallback logic
    search_results = app._auto_search_results(data['message'])
    # Force empty search_results for deterministic behavior
    search_results = [
        {'title':'Result 1','snippet':'Snippet 1','link':'http://example.com/1'},
        {'title':'Result 2','snippet':'Snippet 2','link':'http://example.com/2'},
        {'title':'Result 3','snippet':'Snippet 3','link':'http://example.com/3'}
    ]

    # Simulate LLM call
    response = app.openai_client.create(model='gpt', messages=[])
    print('Mock LLM raw response:', response)
    try:
        raw_json = response.to_dict()
    except Exception:
        raw_json = str(response)
    print('Mock LLM to_dict:', json.dumps(raw_json))

    # Simulate extracted message logic
    llm_message = ''
    if not llm_message or not str(llm_message).strip():
        fallback_lines = []
        for i, r in enumerate(search_results[:3]):
            fallback_lines.append(f"{i+1}. {r.get('title','')} - {r.get('snippet','')} (URL: {r.get('link','')})")
        fallback_text = "I couldn't generate a reply right now. Here are some useful search results I found:\n" + "\n".join(fallback_lines)
        print('Fallback text:')
        print(fallback_text)

if __name__ == '__main__':
    run_mock()
