FROM python:3.10

WORKDIR /

COPY . .

RUN apt-get -y update

RUN pip3 install --no-deps -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["server/docker-entrypoint.sh"]
