from flask import request, jsonify
from flask_restful import Resource


class NodeTagAction(Resource):
    def post(self):
        # 做差集，node_tag接口没有修改和删除
        # 在数据库中把node所有的数据查出来，跟前端传入的tag数组做差集，多的删掉少的加上
        from app import db
        from models.node import NodesHasTag
        from models.tag import Tag
        node = request.json.get('node')
        # tag传入是个数组
        tag = request.json.get('tag')
        # 筛选出体系tag列表
        system_tags = Tag.filter_tags(tag, '体系')
        node_tag_list = NodesHasTag.query.filter_by(nodes_id=node)
        # 校验tag有效性, 一个node最多只能有一个体系tag，业务tag可以有n个
        if len(system_tags) > 1:
            return '体系标签只允许有一个', 400
        if len(system_tags) == 1:
            # node为搜索条件，查询node所属有无体系tag
            for x in node_tag_list:
                if x.tag.type == '体系' and x.tag_id != system_tags[0]:
                    return '不可再添加体系标签', 400
        # 做差集
        tag_history = []
        for x in node_tag_list:
            tag_history.append(x.tag_id)
        add_list = list(set(tag) - set(tag_history))
        delete_list = list(set(tag_history) - set(tag))
        # 增添部分
        for x in add_list:
            insert = NodesHasTag(nodes_id=node, tag_id=x)
            db.session.add(insert)
        # 删除部分
        delete = node_tag_list.filter(NodesHasTag.tag_id.in_(delete_list))
        for x in delete:
            db.session.delete(x)
        db.session.commit()
        return 'success', 200

    def get(self):
        # 根据tag查询node节点
        # TODO 只传入tag_id不传入node_id
        from models.node import NodesHasTag, Node
        # 参数均为列表形式，传入id
        tag = [int(x) for x in request.args.get('tag').split(',')] if request.args.get('tag') else None
        # 若同时存在node和tag的筛选条件，则不能传多个条件
        # if node and tag and (len(node) > 1 and len(tag) > 1):
        #     return '违规操作', 400
        node_tag_list = NodesHasTag.query
        data_return = []
        # 特殊情况已排除，直接遍历筛除即可
        # if node:
        #     node_tag_list = node_tag_list.filter(NodesHasTag.nodes_id.in_(node))
        if tag:
            node_tag_list = NodesHasTag.query.filter(NodesHasTag.tag_id.in_(tag))
        else:
            return '无标签传入', 400
        node_dict = {}
        node_list = []
        result = node_tag_list.all()
        # 组装形式为{node_id_1: [tag_id_1, tag_id_2, tag_id_3], node_id_2: [tag_id_2]}的字典
        for x in result:
            if not node_dict.get(x.nodes_id):
                node_dict[x.nodes_id] = [x.tag_id]
            else:
                if x.tag_id not in node_dict[x.nodes_id]:
                    node_dict[x.nodes_id].append(x.tag_id)
        # 筛选出符合要求的node_id列表
        for key, value in node_dict.items():
            if set(tag) <= set(value):
                node_list.append(key)
        nodes = Node.query.filter(Node.id.in_(node_list))
        # 展开数据
        for x in nodes:
            data_return.append({
                'id': x.id,
                'name': x.name,
                'arch': x.arch_class.name,
                'parallel': x.parallel,
                'online': x.online
            })
        return jsonify(data_return)

    # def delete(self):
    #     from models.node import NodesHasTag
    #     from app import db
    #     node = request.json.get('node')
    #     tag = request.json.get('tag')
    #     node_tag_list = NodesHasTag.query
    #     if node:
    #         node_tag_list = node_tag_list.filter_by(nodes_id=node)
    #     if tag:
    #         node_tag_list = node_tag_list.filter_by(tag_id=tag)
    #     if node or tag:
    #         # 保证带有删除条件，不然会全部删除
    #         db.session.delete(node_tag_list)
    #         db.session.commit()
    #     return 'success', 200


class TagNodeAction(Resource):
    def get(self):
        # 根据node查询tag
        from models.node import NodesHasTag
        from models.tag import Tag
        node = request.args.get('node')
        tag_node_list = NodesHasTag.query
        if node:
            # for x in node:
            tag_node_list = tag_node_list.filter_by(nodes_id=node)
        tag_list = []
        result = tag_node_list.all()
        for x in result:
            tag_list.append(x.tag_id)
        tag_list = list(set(tag_list))
        tags = Tag.query.filter(Tag.id.in_(tag_list))
        data_return = []
        for x in tags:
            data_return.append({
                'id': x.id,
                'name': x.name,
                'type': x.type
            })
        return jsonify(data_return)