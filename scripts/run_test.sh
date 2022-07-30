CREDENTIAL=$1
NUMBER=$2
LANG=$3
TC_NUM=$4
CONTAINER_ID=$5

CRED_PATH="/home/${CREDENTIAL}/${NUMBER}"

if [ $LANG = 'python' ]
then
    sudo docker exec -i --user ${CREDENTIAL} ${CONTAINER_ID} python3 $CRED_PATH/main.py < problems/${NUMBER}/testcases/${TC_NUM}

elif [ $LANG = 'cpp' ] 
then
    sudo docker exec -i --user ${CREDENTIAL} ${CONTAINER_ID} $CRED_PATH/main.out < problems/${NUMBER}/testcases/${TC_NUM}

elif [ $LANG = 'java' ]
then
    sudo docker exec -i --user ${CREDENTIAL} ${CONTAINER_ID} java -cp $CRED_PATH main < problems/${NUMBER}/testcases/${TC_NUM}

elif [ $LANG = 'javascript' ]
then
    sudo docker exec -i --user ${CREDENTIAL} ${CONTAINER_ID} node $CRED_PATH/index.js < problems/${NUMBER}/testcases/${TC_NUM}

elif [ $LANG = 'kotlin' ]
then
    sudo docker exec -i --user ${CREDENTIAL} ${CONTAINER_ID} java -jar $CRED_PATH/main.jar < problems/${NUMBER}/testcases/${TC_NUM}

fi
