FROM python:3.5

ADD ./requirements.txt /home/httpd/requirements.txt
RUN pip install -r /home/httpd/requirements.txt

ADD . /home/httpd/src
WORKDIR /home/httpd/src

RUN chmod +x -R deploy/entry_scripts/

CMD ./deploy/entry_scripts/wait-for-it.sh db:5432 -t 0 -- alembic upgrade head
