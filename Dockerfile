FROM python:3.11-slim

WORKDIR /app/agents

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy agent folder
COPY smart_text_agent/ smart_text_agent/

EXPOSE 8000
CMD ["adk", "web", "--port", "8000", "--host", "0.0.0.0", "."]