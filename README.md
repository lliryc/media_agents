![Llama in the news room](logo.jpg)

![Static Badge](https://img.shields.io/badge/python-3.10_%7C_3.11-blue)  ![GitHub License](https://img.shields.io/github/license/lliryc/media_agents) ![Static Badge](https://img.shields.io/badge/version-0.5.2-orange?logo=github) ![Static Badge](https://img.shields.io/badge/powered_by-LangGraph_%7C_LangChain-magenta?logo=langchain&logoSize=auto)


# Media Agents

Media Agents is a Python-based project that implements Llama-3.1 / GPT4 based LLM assistant which helps journalists to find news leads and materials for news based on [CourtListener](https://www.courtlistener.com/) online base. This system utilizes natural language processing and a graph-based workflow to find newsworthy stories, extract key facts and references, and compose draft with headline from various opinions and sources.

# Contents
1. [Features](#Features)
2. [Prerequisites](#Prerequisites)
3. [Installation](#Installation)
4. [Setup env variables](#Setup-env-variables)
5. [Setup list of subscribers](#Setup-list-of-subscribers)
6. [Run LLM assistant](#Run-LLM-assistant)
7. [Run LLM assistant as a Docker container](#Run-LLM-assistant-as-a-Docker-container)
8. [Contributing](#Contributing)
9. [License](#License)

## Features

- Automated search of newsworthy stories.
- Building support materials: key facts, key entities (mentioned events & locations, involved people & organizations), references to original legal documents.
- Updates by email.

## Prerequisites

Before using Media Agents, ensure you have the following:

- Python 3.10 or higher installed.
- **media_agents** package installed (see the [Installation](#Installation) section).
- Setup env variables.
- Setup email recipients' list.

## Installation

Clone the repository:

```bash
git clone https://github.com/lliryc/media_agents.git
cd media_agents
python3 setup.py install
```

## Setup env variables
The .env file is used to store environment variables that the application needs. Copy and rename [.env.example](.env.example) as **.env** file in the current directory of the project and define values:

```code
LLM_CLIENT=YOUR_LLM_CLIENT_MODEL_NAME # examples: accounts/fireworks/models/llama-v3p1-405b-instruct, gpt-4-turbo
OPENAI_API_KEY=YOUR_OPENAI_API_KEY # for gpt-4 turbo
FIREWORKS_API_KEY=YOUR_FIREWORKS_API_KEY # for llama3.1 405b
SMTP_SERVER=YOUR_SMTP_SERVER # 
SMTP_PORT_SSL=YOUR_SMTP_PORT_SSL
SMTP_USER=YOUR_SMTP_USER
SMTP_PASSWORD=YOUR_SMTP_PASSWORD
```

## Setup list of subscribers
The **recipients.txt** file defines a list of email subscribers. Copy and rename [recipients.txt.example](subscriptions/recipients.txt.example) in **subscriptions** folder as **recipients.txt** and set up your values:

```code
recipient1@example.com  
recipient2@example.com  
recipient3@example.com
```

## Run LLM assistant
To run a program type following command in the console 

```bash
python3 app/app.py
```

After that AI assistant will start processing recent updates from [CourtListener](https://www.courtlistener.com/) portal. Usually it takes about 2-3 hours to process recently published legal documents.
Once all documents was processed, your recepients will get a email with news leads and support materials for news writing.

## Run LLM assistant as a Docker container
To launch a program as a Docker container use following command

```bash
bash start_container.sh
```

Please ensure you logged in on [Docker Hub](https://hub.docker.com/)

## Contributing
Feel free to open issues or submit pull requests if you have suggestions or improvements.

## License
This project is licensed under the  Apache License (Version 2.0, January 2004) - see the [LICENSE](LICENSE) file for details.
