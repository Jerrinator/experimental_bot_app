# Last good deployment


Notes:

Update (2025-08-24T16:22:46Z):

Notes:
- Verified workflow: user input -> helper LLM generates focused search query -> auto-search using that query -> single final LLM call with conversation history and curated search results injected as system context. The runtime logs confirm this flow and assistant responses demonstrate history was available to the model.
- Next issue to address (debut): uploaded documents are not yet reliably injected into the final prompt as "pages in hand". Priority: implement and verify document-context injection into final LLM messages.

Update (2025-08-24T12:13:00Z):
- deployment_id: a209432
- recorded_at_utc: 2025-08-24T12:13:00Z
- branch: master

Notes:
- Commit `a209432` implements injection of user-uploaded documents into the final LLM prompt and messages.
- Uploaded documents are injected as a system-level context block and the model is instructed to treat them as "pages in hand": it should freely discuss, quote, and cite from uploaded documents when relevant to the user's request.
- Default behavior: inject up to 5 most-recent documents (configurable via `MAX_DOCS_TO_INJECT`). By default documents are not truncated; set environment variables to restrict size if desired.
- Edit tracking: EDIT_20250824_114140_923198_0000

Notes:
- Verified workflow: user input -> helper LLM generates focused search query -> auto-search using that query -> single final LLM call with conversation history and curated search results injected as system context. The runtime logs confirm this flow and assistant responses demonstrate history was available to the model.
- Next issue to address (debut): uploaded documents are not yet reliably injected into the final prompt as "pages in hand". Priority: implement and verify document-context injection into final LLM messages.
