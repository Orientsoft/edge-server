from flask import request, jsonify
from flask_restful import Resource


class NodeTagAction(Resource):
    def post(self):
        # 做差集，node_tag接口没有修改和删除
        # 在数据库中把node所有的数据查出来，跟前端传入的tag数组做差集，多的删掉少的加上
        from app import db
        from models.node import NodesHasTag, Node
        from models.tag import Tag
        try:
            node = request.json.get('node')
            # tag传入是个数组
            tag = request.json.get('tag')
            # 筛选出业务tag列表
            tag = Tag.filter_tags(tag, '业务')
            # 查出node所有的业务tag
            # 历史tag
            n = Node.query.get(node)
            tag_history = []
            for x in n.tags:
                if x.type == '业务':
                    tag_history.append(str(x.id))
            add_list = list(set(tag) - set(tag_history))
            delete_list = list(set(tag_history) - set(tag))
            # 增添部分
            for x in add_list:
                insert = NodesHasTag(nodes_id=node, tag_id=x)
                db.session.add(insert)
            # 删除部分
            delete = NodesHasTag.query.filter(NodesHasTag.tag_id.in_(delete_list))
            for x in delete:
                db.session.delete(x)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200


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

