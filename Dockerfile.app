FROM python:3.5

ADD ./requirements.txt /home/httpd/requirements.txt
RUN pip install -r /home/httpd/requirements.txt

ADD . /home/httpd/src
WORKDIR /home/httpd/src
