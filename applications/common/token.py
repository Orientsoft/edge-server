import jwt
import config


def encode_jwt(content):
    # content is JSON objects
    t = jwt.encode(
        content,
        config.SECRET_KEY,
        'HS256'
    )
    return t.decode('utf-8')


def decode_jwt(token):
    obj = jwt.decode(
        token,
        config.SECRET_KEY,
        'HS256'
    )
    return obj
