CREDENTIAL=$1
CONTAINER_ID=$2
sudo docker exec ${CONTAINER_ID} userdel -r ${CREDENTIAL}
sudo docker exec ${CONTAINER_ID} useradd ${CREDENTIAL}
sudo docker cp codes/${CREDENTIAL} ${CONTAINER_ID}:/home/
