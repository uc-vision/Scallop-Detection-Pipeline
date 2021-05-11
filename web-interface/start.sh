#!/bin/bash
app="scallop-upload"
docker run -d -p 56733:80 \
  --name=${app} \
  -v $PWD:/app ${app}
