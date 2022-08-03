CREDENTIAL=$1
CONTAINER_ID=$2
sudo docker exec ${CONTAINER_ID} userdel ${CREDENTIAL} -r
sudo docker exec ${CONTAINER_ID} rm -rf /home/${CREDENTIAL}
