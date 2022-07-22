CREDENTIAL = $1
NUMBER = $1
docker exec test mkdir -p /home/$1
docker cp codes/$1/main.py test:/home/$1
docker exec test python3 /home/$1/main.py < 