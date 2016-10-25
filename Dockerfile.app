FROM python:3.5

ADD . /home/httpd/src
WORKDIR /home/httpd/src

RUN pip install -r requirements.txt

RUN chmod +x -R deploy/entry_scripts/

CMD ./deploy/entry_scripts/wait-for-it.sh db:5432 -t 0 -- alembic upgrade head
