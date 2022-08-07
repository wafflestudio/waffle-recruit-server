CREDENTIAL=$1
CONTAINER_ID=$2
echo "gonna kill as i warned"
# sudo docker exec ${CONTAINER_ID} pkill -9 -u ${CREDENTIAL}
sudo docker restart ${CONTAINER_ID}
