# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
import datetime


class ServiceAction(Resource):
    def post(self):
        from models.service import Service, ServicesHasTag
        from models.tag import Tag
        from app import db, app
        import json
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
        # 校验数据库中，储存k8s的容器名唯一
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

    def get(self):
        from models.service import Service, ServicesHasTag
        import json
        # service 已有的tag
        service_has_tag = ServicesHasTag.get_tag_detail()
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
                "tags": service_has_tag[str(r.id)],
                "kubernetes": json.loads(r.kubernetes),
                "devicemodel": r.devicemodel
            })
        return returnObj

    def patch(self):
        from models.service import Service, ServicesHasTag
        from models.tag import Tag
        from app import db
        id = request.json.get('id')
        s = Service.query.get(id)
        if s:
            name = request.json.get('name', None)
            description = request.json.get('description', None)
            image = request.json.get('image', None)
            tagids = request.json.get('tagids', None)
            if tagids:
                # tag必须是体系类tag。
                tags = Tag.filter_tags(tagids, '体系')
                if not tags:
                    return '标签不能为空', 400
                old_tags = ServicesHasTag.get_tag_ids(id)[id]
                need_delete = list(set(old_tags) - set(tags))
                need_add = list(set(tags) - set(old_tags))
                # 新增标签
                for n in need_add:
                    sht = ServicesHasTag()
                    sht.services_id = id
                    sht.tag_id = n
                    db.session.add(sht)
                # 删除标签
                temp = ServicesHasTag.query.filter(ServicesHasTag.services_id == id,
                                                   ServicesHasTag.tag_id.in_(need_delete)).all()
                for t in temp:
                    db.session.delete(t)
            if name:
                s.name = name
            if description:
                s.description = description
            if image:
                s.image = image
            s.updateAt = datetime.datetime.now()
            db.session.commit()
        else:
            return '服务不存在', 400

    def delete(self):
        from models.service import Service
        from app import db
        id = request.json.get('id')
        s = Service.query.get(id)
        if s:
            db.session.delete(s)
            db.session.commit()
