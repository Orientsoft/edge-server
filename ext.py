# -*- coding:utf-8 -*-
import redis
import config

pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)


def redisHelper():
    return redis.Redis(connection_pool=pool)
