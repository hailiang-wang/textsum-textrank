FROM hain/text-base:latest
MAINTAINER hain@trio.ai

ENV DEBIAN_FRONTEND noninteractive
ENV TAG v1.0.0

RUN apt-get update

# install deps
RUN . /root/venv-py2/bin/activate && pip install flask requests

# copy files
RUN rm -rf /app && mkdir -p /app
COPY ./app/py /app

# touch logs
RUN mkdir /logs && touch /logs/root.log
WORKDIR /app

# specific for run
CMD ["/root/venv-py2/bin/python2", "server.py"]
EXPOSE 10030