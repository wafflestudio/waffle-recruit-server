CREDENTIAL=$1
sudo docker exec test userdel -r ${CREDENTIAL}
sudo docker exec test adduser ${CREDENTIAL}
sudo docker cp codes/${CREDENTIAL} test:/home/