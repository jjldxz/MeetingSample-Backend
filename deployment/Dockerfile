FROM python:3.9.0-slim

LABEL maintainer="liufengyi@jjl.cn"

# using 163 mirror
ADD deployment/sources.list /etc/apt/sources.list

RUN apt-get update && apt-get install -y build-essential libmariadbclient-dev-compat tzdata && apt-get clean && apt-get autoclean
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

ADD . /meeting_sample
WORKDIR /meeting_sample

RUN /usr/local/bin/python -m pip install --no-cache-dir -i https://mirrors.163.com/pypi/simple/ --upgrade pip
RUN pip install --no-cache-dir -i https://mirrors.163.com/pypi/simple/ -r requirements.txt

EXPOSE 80

CMD ["daphne", "-b", "0.0.0.0", "-p", "80", "meeting_sample.asgi:application"]
