from flask import request, jsonify
from flask_restful import Resource
from ext import role_check


class ArchAction(Resource):
    def post(self):
        from app import db
        from models.node import ArchClass
        try:
            name = request.json.get('name')
            interface_name = request.json.get('interface_name')
            podsandbox_image = request.json.get('podsandbox_image')
            tpl = request.json.get('tpl')
            if not name or not interface_name or not podsandbox_image or not tpl:
                print('name: %s, interface_name: %s, podsandbox_image: %s' % (name, interface_name, podsandbox_image))
                return '参数缺失', 400
            insert = ArchClass(name=name, interface_name=interface_name, podsandbox_image=podsandbox_image, tpl=tpl)
            db.session.add(insert)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200

    def get(self):
        from models.node import ArchClass
        id = request.args.get('id')
        name = request.args.get('name')
        interface_name = request.args.get('interface_name')
        class_list = ArchClass.query
        if id:
            class_list = class_list.filter_by(id=id)
        if name:
            class_list = class_list.filter_by(name=name)
        if interface_name:
            class_list = class_list.filter_by(interface_name=interface_name)
        data_return = []
        for x in class_list:
            data_return.append({
                'id': x.id,
                'name': x.name,
                'tpl': x.tpl,
                'interface_name': x.interface_name,
                'podsandbox_image': x.podsandbox_image,
                'package': x.package
            })
        return jsonify(data_return)

    def patch(self):
        from models.node import ArchClass
        from app import db
        try:
            id = request.json.get('id')
            name = request.json.get('name')
            interface_name = request.json.get('interface_name')
            podsandbox_image = request.json.get('podsandbox_image')
            tpl = request.json.get('tpl')
            if not id:
                return '参数缺失', 400
            node_class = ArchClass.query.get(id)
            if not node_class:
                return '无效的id', 400
            if name:
                node_class.name = name
            if interface_name:
                node_class.interface_name = interface_name
            if podsandbox_image:
                node_class.podsandbox_image = podsandbox_image
            if tpl:
                node_class.tpl = tpl
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200

    @role_check
    def delete(self):
        from models.node import ArchClass
        from app import db
        try:
            id = request.json.get('id')
            if not id:
                return '参数缺失', 400
            node_class = ArchClass.query.get(id)
            if not node_class:
                return '无效的id', 400
            db.session.delete(node_class)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200
