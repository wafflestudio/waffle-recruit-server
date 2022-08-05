#celery -A waffle_recruit_server worker -l info -c 1
#python3 -m celery -A waffle_recruit_server worker -l info -c 1 &
python3 -m celery -A waffle_recruit_server worker -l info -c 4 &
