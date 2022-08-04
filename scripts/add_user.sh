CREDENTIAL=$1
CONTAINER_ID=$2
echo "from adduser1"
sudo docker exec ${CONTAINER_ID} userdel -r -f ${CREDENTIAL}
sudo docker exec ${CONTAINER_ID} useradd ${CREDENTIAL}
echo "from adduser2"
# sudo docker exec ${CONTAINER_ID} chmod 555 /home/${CREDENTIAL}
sudo docker cp codes/${CREDENTIAL} ${CONTAINER_ID}:/home/
