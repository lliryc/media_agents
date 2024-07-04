# Media Agents

This repository contains a project that processes court opinions to determine their newsworthiness based on several criteria. 

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [License](#license)

## Introduction

The Media Agents project processes court opinion files to evaluate their potential newsworthiness. This is achieved by using intelligent agents empowered with large language models to assess the opinions based on different factors.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/lliryc/media_agents.git
    cd media_agents
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Optional: Set up your OpenAI API key by creating a `.env` file in the project root directory with the following content:

    ```env
    OPENAI_API_KEY=your_openai_api_key
    ```

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
