FROM python:3.6-alpine as base
FROM base as builder
# RUN apk add --no-cache gcc musl-dev
RUN apk --no-cache add \
                       # Pillow dependencies
                       jpeg-dev \
                       zlib-dev \
                       freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       harfbuzz-dev \
                       fribidi-dev \
                       gcc \
                       musl-dev \
                       g++ \
                       libc-dev \
                       linux-headers \
                       mariadb-dev \
                       python3-dev \
                       postgresql-dev \
                       mysql-dev \
                       libffi-dev \
                       openssl-dev

RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install" -r /requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

FROM base
RUN apk --no-cache add jpeg-dev \
                       zlib-dev \
                       freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       harfbuzz-dev \
                       fribidi-dev


COPY --from=builder /install /usr/local
WORKDIR /app
COPY applications ./applications
COPY models ./models
COPY *.py ./
# COPY config.yaml .

CMD [ "python", "app.py"]