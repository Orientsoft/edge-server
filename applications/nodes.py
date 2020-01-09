from flask import request, jsonify, make_response
from flask_restful import Resource


class NodeAction(Resource):
    def post(self):
        from app import db
        from datetime import datetime
        from models.node import Node, NodesHasTag
        from models.tag import Tag
        from applications.common.k8s import create_node
        import time
        import hashlib
        name = request.json.get('name')
        parallel = request.json.get('parallel', 1)
        arch_class_id = request.json.get('arch_class_id')
        count = request.json.get('count', 1)
        tag = request.json.get('tag_id')
        try:
            # 校验tag是否为体系tag
            tag_model = Tag.query.get(tag)
            if tag_model.type != '体系':
                return '必须选择体系标签', 400
            result = Node.query.filter_by(name=name).first()
            if result:
                return '节点名重复', 400
            # 校验name唯一性，并且只能为小写英文
            for x in name:
                if ord(x) < 97 or ord(x) > 122:
                    return '节点名只能为小写英文', 400
        except Exception as e:
            print(e)
            return '后台异常', 500
        for x in range(count):
            token_before = name + '-' + str(x) + str(time.time())
            h = hashlib.md5()
            h.update(token_before.encode('utf-8'))
            token = h.hexdigest()
            insert = Node(name=name + '-' + str(x), parallel=parallel, online=False, updatedAt=datetime.now(),
                          createdAt=datetime.now(), arch_class_id=arch_class_id, token=token)
            db.session.add(insert)
            # 调用k8s起节点
            create_status = create_node(name + '-' + str(x))
            if not create_status:
                return '创建节点失败', 400
            db.session.flush()
            # 查出node_id后添加node_tag关系
            insert = NodesHasTag(nodes_id=insert.id, tag_id=tag)
            db.session.add(insert)
        db.session.commit()
        return 'success', 200

    def get(self):
        from models.node import Node
        from applications.common.k8s import update_node_online_status
        id = request.args.get('id')
        name = request.args.get('name')
        parallel = int(request.args.get('parallel')) if request.args.get('parallel') else None
        online = request.args.get('online')
        # arch_class_id = request.args.get('arch_class_id')
        page = request.args.get('page', 1)
        pageSize = request.args.get('pageSize', 20)
        # 更新node的online状态
        update_node_online_status()
        node_list = Node.query
        if id:
            node_list = node_list.filter_by(id=id)
        if name:
            node_list = node_list.filter_by(name=name)
        if parallel:
            node_list = node_list.filter_by(parallel=parallel)
        if online:
            node_list = node_list.filter_by(online=online)
        # if arch_class_id:
        #     node_list = node_list.filter_by(arch_class_id=arch_class_id)
        # 分页
        node_list = node_list.limit(pageSize).offset((page - 1) * pageSize)
        data_return = []
        for x in node_list:
            data_return.append({
                'id': x.id,
                'name': x.name,
                'parallel': x.parallel,
                'online': x.online,
                'arch_class_id': x.arch_class_id,
                'arch_class_name': x.arch_class.name,
                'updatedAt': x.updatedAt,
                'createdAt': x.createdAt,
                'url': '/deploy?token=%s' % x.token
            })
        return jsonify(data_return)

    def patch(self):
        from models.node import Node
        from datetime import datetime
        from app import db
        id = request.json.get('id')
        # name = request.json.get('name')
        parallel = request.json.get('parallel')
        # online = request.json.get('online')
        # node_class_id不给改
        # nodeClass = request.json.get('nodeClassId')
        if not id:
            return '参数错误', 400
        node_model = Node.query.get(id)
        if not node_model:
            return '无效的id', 400
        # if name:
        #     node_model.name = name
        if parallel:
            node_model.parallel = parallel
        # if online:
        #     node_model.online = online
        node_model.updatedAt = datetime.now()
        db.session.commit()
        return 'success', 200

    # def delete(self):
    #     from models.node import Node
    #     from app import db
    #     id = request.json.get('id')
    #     if not id:
    #         return '参数错误', 400
    #     node_model = Node.query.get(id)
    #     if not node_model:
    #         return '无效的id', 400
    #     db.session.delete(node_model)
    #     db.session.commit()
    #     return 'success', 200


class NodeDeployLink(Resource):
    def get(self):
        from models.node import Node
        token = request.args.get('token')
        n = Node.query.filter_by(token=token).first()
        if not n:
            return 'node不存在', 400
        with open('edge.sh') as f:
            download_content = f.read()
        resp = make_response(self.format_sh(download_content, n))
        resp.headers['Content-Disposition'] = ("attachment; filename='{0}'; filename*=UTF-8''{0}".format('edge.sh'))
        resp.headers['Content-Type'] = 'application/octet-stream'
        return resp

    @staticmethod
    def format_sh(line, n):
        from app import app
        from applications.common.s3 import presign_url
        package_name = n.arch_class.package.replace('package/', '').replace('.tar.gz', '')
        line = line.replace('package_address', presign_url(n.arch_class.package))
        line = line.replace('package_name', package_name)
        line = line.replace('yaml_address', presign_url(n.arch_class.tpl))
        line = line.replace('socket_config', app.config['WEBSOCKET_URL'])
        line = line.replace('node_id_config', n.name)
        line = line.replace('interface_config', n.arch_class.interface_name)
        line = line.replace('image_config', n.arch_class.podsandbox_image)
        line = line.replace('crt_address', presign_url(app.config['CERT_CRT']))
        line = line.replace('key_address', presign_url(app.config['CERT_KEY']))
        return line
