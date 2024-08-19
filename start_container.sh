CURRENT_DIR=$(pwd)
docker run \
  --name media_agents_container \
  -v $CURRENT_DIR/.env:/media_agents/.env \
  -v $CURRENT_DIR/subscriptions/recipients.txt:/media_agents/subscriptions/recipients.txt \
  docker.io/chelliryc/media_agents:v0.5.1