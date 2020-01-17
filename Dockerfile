FROM python:3.6-alpine
RUN apk add --no-cache gcc musl-dev g++ mysql-dev mariadb-dev openblas-dev libffi-dev python3-dev

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

WORKDIR /app
COPY applications ./applications
COPY models ./models
COPY *.py ./
COPY edge.sh ./edge.sh


CMD [ "python", "app.py"]