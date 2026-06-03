# 📝 SmartText Agent — Multi-Capability AI Text Processor

> Five text-processing capabilities unified under one Gemini-powered agent with intelligent intent routing.

**Live Demo:** https://smart-text-agent-381066349460.us-central1.run.app

Built for the **Google Cloud Gen AI Academy APAC Edition** — Track 1 Submission.

---

## What is SmartText Agent?

A multi-capability AI agent built with **Google ADK** and **Gemini 2.5 Flash**. It exposes five tools and uses trigger-word detection plus an explicit `route_request` tool to auto-pick the right capability for ambiguous queries.

Ask it anything:
- *"Summarize: Cloud computing is the delivery of computing services..."*
- *"What is Kubernetes and why is it used?"*
- *"Classify: Virat Kohli smashed a brilliant century to guide India to victory."*
- *"Analyze: The quick brown fox jumps over the lazy dog."*
- *"Help me with this: Docker containers package applications..."* (auto-routes)

---

## 🏗️ Architecture

![SmartText Agent Architecture](https://github.com/VishwasPrabhakara/smart-text-agent/raw/main/architecture.svg)

---

## 🔧 Five Capabilities

| Tool | Description | Example |
|------|-------------|---------|
| `summarize_text` | Concise (2-3 sentences), detailed (paragraph), or bullet styles. Skips text under 20 words. Reports original vs. summary word count. | `style: "concise" \| "detailed" \| "bullet"` |
| `answer_question` | Factual, explanatory, comparative, advisory, or enumerative. Optional `context` for grounded answers. Auto-detects question type. | `question, context (optional)` |
| `classify_text` | 9 categories — Technology, Sports, Politics, Science, Health, Business, Entertainment, Education, Other. Keyword pre-detection helps Gemini reason. | `text` |
| `analyze_text` | Word count, sentence count, character count, average word length, estimated reading time (words ÷ 4.2 wpm). | `text` |
| `route_request` | Auto-detects intent from trigger words (summarize / classify / question) and recommends the right tool. The agent then calls it. | `request` |

The agent's system prompt enforces **"ALWAYS call a tool before responding."**

---

## 🛠️ Tech Stack

- **google-adk** (`==1.14.0`) — Agent Development Kit, tool framework
- **Gemini 2.5 Flash** (`gemini-2.5-flash`) — function calling + response generation
- **Python 3.11**
- **Docker** — `python:3.11-slim` base
- **Google Cloud Run** — serverless, scale-to-zero
- **Cloud Build + Artifact Registry** — CI/CD

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11+
- Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Setup
```bash
git clone https://github.com/VishwasPrabhakara/smart-text-agent.git
cd smart-text-agent

pip install -r requirements.txt

# Create .env (used by ADK to pick up the key)
cat > .env <<EOF
GOOGLE_API_KEY=your_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
EOF

adk web --port 8000 --host 0.0.0.0 .
```

Open `http://localhost:8000` and pick `smart_text_agent` in the dropdown.

---

## 🐳 Deploy to Cloud Run

The repo uses the ADK CLI's built-in Cloud Run deploy:

```bash
gcloud config set project YOUR_PROJECT_ID

uvx --from google-adk==1.14.0 adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --service_name=smart-text-agent \
  --with_ui .
```

The deployed service URL is printed after deployment. Make sure `GOOGLE_API_KEY` and `GOOGLE_GENAI_USE_VERTEXAI=FALSE` are set as env vars on the Cloud Run service.

---

## 📁 Project Structure

```
smart-text-agent/
├── Dockerfile
├── requirements.txt        # google-adk==1.14.0
├── README.md
├── architecture.svg
├── .env                    # GOOGLE_API_KEY (not committed)
└── smart_text_agent/
    ├── __init__.py         # exports root_agent
    └── agent.py            # 5 tool functions + Gemini agent definition
```

---

## 💡 How It Works

1. **User sends a query** via the ADK web UI
2. **Gemini 2.5 Flash** reads the system prompt's trigger-word rules and picks a tool
3. **The tool function** runs deterministic prep (word counts, keyword hints, question-type detection) and returns structured JSON
4. **For ambiguous queries:** `route_request` is called first → returns `recommended_tool` → the agent then calls that tool
5. **Gemini formats the structured result** into a clean, prose response

The deterministic-prep + LLM-formatting split keeps classifications consistent and analyses accurate, while letting Gemini handle the natural-language packaging.

---

## 📝 Built For

Google Cloud Gen AI Academy APAC Edition — Track 1 Submission
**Built by:** Vishwas Prabhakara

## 📄 License

MIT
