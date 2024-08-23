# Media Agents

Media Agents is a Python-based project that implements AI assistant which helps journalists to find news leads and materials for news based on CourtListener online base. This system utilizes natural language processing and a graph-based workflow to find newsworthy stories, extract key facts and references, and compose draft with headline from various opinions and sources.

## Features

- Automated search of newsworthy stories.
- Building support materials: key facts, key entities (mentioned events & locations, involved people & organizations), references to original legal documents.
- Updates by email.

## Prerequisites

Before using Media Agents, ensure you have the following:

- Python 3.10 or higher installed.
- Required Python packages (see the Installation section).
- Setup env variables
- Define email recipients' list.

## Installation

Clone the repository:

```bash
git clone https://github.com/lliryc/media_agents.git
cd media_agents
python setup.py install
```

## Setup env variables
The .env file is used to store environment variables that the application needs. Copy and rename a .env.example as .env file in the current directory of the project and define values:

```code
LLM_CLIENT=YOUR_LLM_CLIENT_MODEL_NAME # examples: accounts/fireworks/models/llama-v3p1-405b-instruct, gpt-4-turbo
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
GROQ_API_KEY=YOU_GROQ_API_KEY
FIREWORKS_API_KEY=YOUR_FIREWORKS_API_KEY
SMTP_SERVER=YOUR_SMTP_SERVER
SMTP_PORT_SSL=YOUR_SMTP_PORT_SSL
SMTP_USER=YOUR_SMTP_USER
SMTP_PASSWORD=YOUR_SMTP_PASSWORD
```
