#!/bin/bash

set -exuo pipefail

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 799634405166.dkr.ecr.eu-central-1.amazonaws.com
docker build -t coder/agentic-ai-nano .
docker tag coder/agentic-ai-nano:latest 799634405166.dkr.ecr.eu-central-1.amazonaws.com/coder/agentic-ai-nano:latest
docker push 799634405166.dkr.ecr.eu-central-1.amazonaws.com/coder/agentic-ai-nano:latest
