# coding: utf-8
from app import db


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45))
    type = db.Column(db.Enum('业务', '体系'))

    nodes = db.relationship('Node', secondary='nodes_has_tag')
    services = db.relationship('Service', secondary='services_has_tag')

    @staticmethod
    def filter_tags(tagids, type):
        tags = []
        try:
            tagResult = Tag.query.filter(Tag.id.in_(tagids), Tag.type == type).all()
            for t in tagResult:
                tags.append(str(t.id))
        except:
            pass
        finally:
            return tags
