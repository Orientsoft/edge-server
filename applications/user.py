from flask import request, session
from flask_restful import Resource


class UserAction(Resource):
    def post(self):
        from app import app
        name = request.json.get('name')
        key = request.json.get('key')
        if name != app.config['USER'].split(':')[0] or key != app.config['USER'].split(':')[1]:
            return '登陆失败', 400
        else:
            session['name'] = name
            return '登陆成功', 200
