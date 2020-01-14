# -*- coding:utf-8 -*-
# from functools import wraps
import redis
import config

pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)


def redisHelper():
    return redis.Redis(connection_pool=pool)


# def role_check(role_list):
#     def role_decorator(f):
#         @wraps(f)
#         def role_function(*args, **kwargs):
#             # print(session.get('role'))
#             # if not session.get('role') and session.get('role') != 0:
#             #     return '请登录', 403
#             # elif session.get('role') not in role_list:
#             #     return '权限不足', 400
#             return '权限不足', 400
#
#         return role_function
#
#     return role_decorator
