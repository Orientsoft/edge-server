# coding: utf-8
from app import db


class ArchClass(db.Model):
    __tablename__ = 'arch_class'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45))
    tpl = db.Column(db.String(500))
    interface_name = db.Column(db.String(45))
    podsandbox_image = db.Column(db.String(45))
    package = db.Column(db.String(45))


class Node(db.Model):
    __tablename__ = 'nodes'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45))
    parallel = db.Column(db.INTEGER)
    online = db.Column(db.Boolean)
    updatedAt = db.Column(db.DateTime)
    createdAt = db.Column(db.DateTime)
    arch_class_id = db.Column(db.ForeignKey('arch_class.id'), nullable=False, index=True)
    token = db.Column(db.String(45))

    arch_class = db.relationship('ArchClass')


class NodesHasTag(db.Model):
    __tablename__ = 'nodes_has_tag'

    nodes_id = db.Column(db.ForeignKey('nodes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    tag_id = db.Column(db.ForeignKey('tag.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    id = db.Column(db.INTEGER, primary_key=True)

    nodes = db.relationship('Node')
    tag = db.relationship('Tag')

    @staticmethod
    def available_node(node_ids, services_id):
        result = []
        nodes = {}
        from models.service import ServicesHasTag
        try:
            resultObj = ServicesHasTag.query.filter_by(services_id=services_id).all()
            must_tags = []
            for r in resultObj:
                must_tags.append(r.tag_id)
            dataObj = NodesHasTag.query.filter(NodesHasTag.nodes_id.in_(node_ids)).all()
            for d in dataObj:
                if d.tag.type == '体系' and d.tag_id in must_tags:
                    result.append(str(d.nodes_id))
                    nodes[str(d.nodes_id)] = d.nodes.name
        except:
            pass
        finally:
            return result,nodes


class NodesHasTask(db.Model):
    __tablename__ = 'nodes_has_task'

    nodes_id = db.Column(db.ForeignKey('nodes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    task_id = db.Column(db.ForeignKey('task.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    id = db.Column(db.INTEGER, primary_key=True)
    device_name = db.Column(db.String(45))

    nodes = db.relationship('Node')
    task = db.relationship('Task')

    @staticmethod
    def get_node_ids(task_id):
        result = []
        try:
            dataObj = NodesHasTask.query.filter_by(task_id=task_id).all()
            for d in dataObj:
                result.append(str(d.nodes_id))
        except:
            pass
        finally:
            return result
