#!/bin/sh

docker run -d -p 11400:11400 --name ollama ollama/ollama:latest
OPENSEARCH_INITIAL_ADMIN_PASSWORD=$(openssl rand -base64 32)
echo "$OPENSEARCH_INITIAL_ADMIN_PASSWORD" > opensearch_password.txt
docker run -d -p 9200:9200 -p 9600:9600 --name opensearch \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=$OPENSEARCH_INITIAL_ADMIN_PASSWORD" \
  -e "discovery.type=single-node" \
  -e "plugins.security.ssl.http.enabled=false" \
  opensearchproject/opensearch:latest