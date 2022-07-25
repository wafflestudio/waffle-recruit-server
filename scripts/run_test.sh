#!/bin/bash

echo "PONG 1 FROM RUN_TEST"

# CREDENTIAL=$1
# NUMBER=$2
# LANG=$3
# TC_NUM=$4

# CRED_PATH="home/${CREDENTIAL}/${NUMBER}"

# if [ $LANG = 'python' ]
# then
#     # sudo docker exec -i --user ${CREDENTIAL} test python3 $CRED_PATH/main.py < problems/${NUMBER}/testcases/${TC_NUM}
#     sudo docker exec --user ${CREDENTIAL} test python3 $CRED_PATH/main.py
#     echo "PONG 2 FROM RUN_TEST"

# elif [ $LANG = 'cpp' ]
# then
#     sudo docker exec --user ${CREDENTIAL} test $CRED_PATH/main.out

# elif [ $LANG = 'java' ]
# then
#     sudo docker exec --user ${CREDENTIAL} test java -cp $CRED_PATH/Main

# elif [ $LANG = 'javascript' ]
# then
#     sudo docker exec --user ${CREDENTIAL} test node $CRED_PATH

# elif [ $LANG = 'kotlin' ]
# then
#     sudo docker exec --user ${CREDENTIAL} test java -jar $CRED_PATH/Main

# fi
