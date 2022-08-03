sudo docker rm -f test1
sudo docker rm -f test2
sudo docker rm -f test3
sudo docker rm -f test4
sudo docker rm -f test5
sudo docker rm -f test6
sudo docker rm -f test7
sudo docker rm -f test8






sudo docker create -it --network none --name test1 whizkyu/recruit:1.1 > /dev/null
sudo docker create -it --network none --name test2 whizkyu/recruit:1.1 > /dev/null
sudo docker create -it --network none --name test3 whizkyu/recruit:1.1 > /dev/null
sudo docker create -it --network none --name test4 whizkyu/recruit:1.1 > /dev/null
sudo docker create -it --network none --name test5 whizkyu/recruit:1.1 > /dev/null
sudo docker create -it --network none --name test6 whizkyu/recruit:1.1 > /dev/null
sudo docker create -it --network none --name test7 whizkyu/recruit:1.1 > /dev/null
sudo docker create -it --network none --name test8 whizkyu/recruit:1.1 > /dev/null
sudo docker start test1 > /dev/null
sudo docker start test2 > /dev/null
sudo docker start test3 > /dev/null
sudo docker start test4 > /dev/null
sudo docker start test5 > /dev/null
sudo docker start test6 > /dev/null
sudo docker start test7 > /dev/null
sudo docker start test8 > /dev/null

# https://kimjingo.tistory.com/60 -> cpu 자원 제어 가능
