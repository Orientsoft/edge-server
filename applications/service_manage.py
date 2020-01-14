# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
from ext import role_check
import datetime
import json


class ServiceAction(Resource):
    def post(self):
        from models.service import Service, ServicesHasTag
        from models.tag import Tag
        from app import db, app
        try:
            s = Service()
            # tagids = ['1','2','3']
            tagids = request.json.get('tagids', [])
            # tag必须是体系类tag。
            tags = Tag.filter_tags(tagids, '体系')
            if not tags:
                return '标签是必选项', 400
            s.name = request.json.get('name')
            s.description = request.json.get('description')
            s.image = request.json.get('image')
            kubernetes = request.json.get('kubernetes')
            s.kubernetes = json.dumps(kubernetes)
            s.devicemodel = app.config['DEVICEMODEL']
            s.createdAt = datetime.datetime.now()
            db.session.add(s)
            db.session.flush()
            # 新建service时指定tag
            for t in tags:
                sht = ServicesHasTag()
                sht.services_id = s.id
                sht.tag_id = t
                db.session.add(sht)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200

    def get(self):
        from models.service import Service, ServicesHasTag
        import json
        resultObj = Service.query.all()
        returnObj = []
        for r in resultObj:
            returnObj.append({
                "id": str(r.id),
                "name": r.name,
                "description": r.description,
                "image": r.image,
                "createdAt": r.createdAt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(r.createdAt,
                                                                                     datetime.datetime) else r.createdAt,
                "updateAt": r.updateAt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(r.updateAt,
                                                                                   datetime.datetime) else r.updateAt,
                "tags": list(map(lambda x: {'id': x.id, 'name': x.name}, r.tags)),
                "kubernetes": json.loads(r.kubernetes),
                "devicemodel": r.devicemodel
            })
        return returnObj

    def patch(self):
        from models.service import Service
        from app import db
        try:
            id = request.json.get('id')
            s = Service.query.get(id)
            # import 不可变更tagid
            if s:
                name = request.json.get('name', None)
                description = request.json.get('description', None)
                image = request.json.get('image', None)
                kubernetes = request.json.get('kubernetes', None)
                if name:
                    s.name = name
                if description:
                    s.description = description
                if image:
                    s.image = image
                if kubernetes:
                    s.kubernetes = json.dumps(image)
                s.updateAt = datetime.datetime.now()
                db.session.commit()
            else:
                return '服务不存在', 400
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200

    @role_check
    def delete(self):
        from models.service import Service
        from app import db
        try:
            id = request.json.get('id')
            s = Service.query.get(id)
            if s:
                db.session.delete(s)
                db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return '已有任务使用该服务，无法删除', 400
        return 'success', 200


class ServiceNodeAction(Resource):
    def get(self, service_id):
        from models.service import ServicesHasTag, Service
        from models.node import NodesHasTag, Node
        result = []
        s = Service.query.get(service_id)
        if not s:
            return '服务不存在', 400
        # 服务支持的tag
        tagids = list(map(lambda x: str(x.id), s.tags))  # ['1','2']
        # tag对应的node
        nodeids = []
        dataObj = NodesHasTag.query.filter(NodesHasTag.tag_id.in_(tagids)).all()
        for d in dataObj:
            nodeids.append(d.nodes_id)
        nodeObj = Node.query.filter(Node.id.in_(nodeids)).all()
        for d in nodeObj:
            result.append({
                "id": d.id,
                "name": d.name,
                "arch": d.arch_class.name,
                "parallel": d.parallel,
                "online": d.online,
                "tags":list(map(lambda y: {'id': y.id, 'name': y.name}, d.tags)),
                "createdAt": d.createdAt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(d.createdAt,
                                                                                           datetime.datetime) else d.createdAt,
            })
        return result
