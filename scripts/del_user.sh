CREDENTIAL=$1
sudo docker exec test userdel -r ${CREDENTIAL}
sudo docker exec test rm -rf /home/${CREDENTIAL}