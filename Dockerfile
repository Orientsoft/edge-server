FROM python:3.6-alpine as base
FROM base as builder
RUN apk add --no-cache gcc musl-dev g++ mysql-dev mariadb-dev openblas-dev libffi-dev python3-dev


RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install" -r /requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

FROM base
COPY --from=builder /install /usr/local
WORKDIR /app
COPY applications ./applications
COPY models ./models
COPY *.py ./
COPY edge.sh ./edge.sh


CMD [ "python", "app.py"]