CREDENTIAL=$1
CONTAINER_ID=$2
echo "DELETE ${CREDENTIAL}"
sudo docker exec ${CONTAINER_ID} pkill -u ${CREDENTIAL}
sudo docker exec ${CONTAINER_ID} userdel -r ${CREDENTIAL}
sudo docker exec ${CONTAINER_ID} rm -rf /home/${CREDENTIAL}
