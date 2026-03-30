# SmartText Agent

AI-powered multi-capability text processing agent built with Google ADK and Gemini 2.5 Flash, deployed on Cloud Run.

## Capabilities
1. **Text Summarization** — Concise, detailed, or bullet-point summaries
2. **Question Answering** — Context-based or general knowledge Q&A
3. **Text Classification** — Categorizes text with keyword-assisted reasoning
4. **Text Analysis** — Word count, reading time, and text statistics
5. **Smart Routing** — Auto-detects user intent for ambiguous requests

## Tech Stack
- Google ADK v1.14.0
- Gemini 2.5 Flash
- Google Cloud Run
- Python 3.12

## Project Structure
```
smart_text_agent/
├── .env                 # API config (not in repo)
├── requirements.txt
├── README.md
└── summarizer/
    ├── __init__.py
    └── agent.py         # Agent with 5 tools
```

## Deploy
```bash
gcloud config set project YOUR_PROJECT_ID
uvx --from google-adk==1.14.0 adk deploy cloud_run \
  --project=$PROJECT_ID --region=us-central1 \
  --service_name=smart-text-agent --with_ui .
```

## Author
Built for Gen AI Academy APAC Edition — Track 1
