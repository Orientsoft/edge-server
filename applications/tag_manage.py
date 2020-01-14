# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
# from ext import role_check
import json


class TagAction(Resource):
    def post(self):
        from models.tag import Tag
        from app import db
        try:
            t = Tag()
            t.name = request.json.get('name')
            t.type = request.json.get('type')
            db.session.add(t)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200

    def get(self):
        from models.tag import Tag
        name = request.args.get('name', None)
        type = request.args.get('type', None)
        dataObj = Tag.query
        if name:
            dataObj = dataObj.filter_by(name=name)
        if type:
            dataObj = dataObj.filter_by(type=type)
        resultObj = dataObj.all()
        returnObj = []
        for r in resultObj:
            returnObj.append({
                "id": str(r.id),
                "name": r.name,
                "type": r.type,
                "nodes": list(map(lambda x: {'id': x.id, 'name': x.name, 'online': x.online, 'parallel': x.parallel,
                                             'arch': x.arch_class.name}, r.nodes)),
                "services": list(map(
                    lambda x: {'id': x.id, 'name': x.name, 'description': x.description, 'image': x.image,
                               'kubernetes': json.loads(x.kubernetes)}, r.services))
            })
        return returnObj

    def patch(self):
        from models.tag import Tag
        from app import db
        try:
            id = request.json.get('id')
            t = Tag.query.get(id)
            if t:
                name = request.json.get('name', None)
                if name:
                    t.name = name
                # IMPORT IMPORT IMPORT type 不可变更
                db.session.commit()
            else:
                return '标签不存在', 400
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200

    # @role_check
    def delete(self):
        from models.tag import Tag
        from app import db
        try:
            id = request.json.get('id')
            t = Tag.query.get(id)
            if t:
                db.session.delete(t)
                db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return '标签已被使用，无法删除', 400
        return 'success', 200
