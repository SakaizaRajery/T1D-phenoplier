#/bin/bash

PROJECT_NAME="phenoplier"
VERSION="1.2"

docker build -t miltondp/${PROJECT_NAME}:${VERSION} -t miltondp/${PROJECT_NAME}:latest .

read -p "'docker push' new image? " -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # push version label
  docker push miltondp/${PROJECT_NAME}:${VERSION}

  # push latest label
  docker push miltondp/${PROJECT_NAME}:latest

  # update description (short 100 chars)
  # update README.md in Docker Hub
fi

