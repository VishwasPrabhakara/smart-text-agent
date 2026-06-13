# Security Policy

## Reporting

Report suspected vulnerabilities privately through GitHub's security advisory
feature. Do not include credentials in a public issue.

## Data and credentials

- Never commit `.env` or API keys.
- User text is sent to Gemini when the agent runs.
- The repository does not implement application-level authentication, durable
  storage, or redaction.
- The bundled ADK web UI is intended for demonstration and testing. Add access
  controls before exposing a deployment to sensitive or untrusted traffic.
- Rotate any credential immediately if it is exposed.
