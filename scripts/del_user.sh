CREDENTIAL=$1
CONTAINER_ID=$2
echo "yahoo"
sudo docker exec ${CONTAINER_ID} userdel ${CREDENTIAL} -r
sudo docker exec ${CONTAINER_ID} rm -rf /home/${CREDENTIAL}
