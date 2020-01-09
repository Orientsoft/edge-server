# /usr/bin/python
# -*- coding:utf-8 -*-
import boto3
from io import BytesIO
import datetime
import config
import uuid

s3 = boto3.client('s3', aws_access_key_id=config.S3_ACCESS,
                  aws_secret_access_key=config.S3_SECRET)


# AWS 上传和获取url
def Upload_AWS(file):
    try:
        st = file.stream.read()
        data = BytesIO(st)
        attr = file.filename.rsplit('.', 1)
        day = (datetime.datetime.now()).strftime('%Y-%m-%d')
        nonce = uuid.uuid1().hex
        # /日期/原文件名+uuid.jpg
        filename = '{}/{}@{}.jpg'.format(day, attr[0], nonce)
        s3.put_object(Key=filename, Bucket=config.S3_BUCKET, Body=data, ContentType='image/jpeg')
        return filename
    except Exception as e:
        return -1


def presign_url(filekey):
    url = s3.generate_presigned_url('get_object', Params={'Bucket': config.S3_BUCKET,
                                                          'Key': filekey},
                                    ExpiresIn=config.S3_EXPIRE, HttpMethod='GET')
    return url