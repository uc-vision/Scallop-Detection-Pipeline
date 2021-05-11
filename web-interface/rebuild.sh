app="scallop-upload"
docker stop ${app}
docker rm ${app}
docker rmi ${app}
docker build -t ${app} .
