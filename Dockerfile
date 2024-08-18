# Use the official slim Python image as a base image
FROM python:3.11-slim

# Define the directory path as a variable
ENV MEDIA_AGENTS_DIR=/media_agents

# Set the working directory inside the container
WORKDIR $MEDIA_AGENTS_DIR

# Copy only the files needed for installation first to leverage Docker cache
COPY requirements.txt setup.py $MEDIA_AGENTS_DIR/

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application files using the variable
COPY media_agents/ $MEDIA_AGENTS_DIR/media_agents/
COPY app/ $MEDIA_AGENTS_DIR/app/
COPY state/ $MEDIA_AGENTS_DIR/state/
COPY subscriptions/ $MEDIA_AGENTS_DIR/subscriptions/
COPY .env.example $MEDIA_AGENTS_DIR/.env
COPY LICENSE $MEDIA_AGENTS_DIR/LICENSE
COPY log_config.json $MEDIA_AGENTS_DIR/log_config.json
COPY logging_init.py $MEDIA_AGENTS_DIR/logging_init.py
COPY README.md $MEDIA_AGENTS_DIR/README.md

# Install the application package
RUN pip3 install .

# Specify the command to run your application
CMD ["python3", "-m", "app.app"]
