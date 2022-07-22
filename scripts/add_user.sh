CREDENTIAL=$1
sudo docker exec test adduser ${CREDENTIAL}
sudo docker cp codes/${CREDENTIAL} test:/home/