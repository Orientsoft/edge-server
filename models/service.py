# coding: utf-8
from app import db


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45))
    description = db.Column(db.String(200))
    image = db.Column(db.String(100))
    createdAt = db.Column(db.DateTime)
    updateAt = db.Column(db.DateTime)
    devicemodel = db.Column(db.String(45))
    kubernetes = db.Column(db.String(2000))


class ServicesHasTag(db.Model):
    __tablename__ = 'services_has_tag'

    services_id = db.Column(db.ForeignKey('services.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                            index=True)
    tag_id = db.Column(db.ForeignKey('tag.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    id = db.Column(db.INTEGER, primary_key=True)

    services = db.relationship('Service')
    tag = db.relationship('Tag')

    @staticmethod
    def get_tag_detail(service_id=None):
        result = {}
        try:
            dataObj = ServicesHasTag.query
            if service_id:
                dataObj = dataObj.filter_by(services_id=service_id).all()
            else:
                dataObj = dataObj.all()
            for d in dataObj:
                temp = {'tag_id': str(d.tag_id), 'tag_name': d.tag.name}
                if str(d.services_id) in result:
                    result[str(d.services_id)].append(temp)
                else:
                    result[str(d.services_id)] = [temp]
        except:
            pass
        finally:
            return result

    @staticmethod
    def get_tag_ids(service_id=None):
        result = {}
        try:
            dataObj = ServicesHasTag.query
            if service_id:
                dataObj = dataObj.filter_by(services_id=service_id).all()
            else:
                dataObj = dataObj.all()
            for d in dataObj:
                if str(d.services_id) in result:
                    result[str(d.services_id)].append(str(d.tag_id))
                else:
                    result[str(d.services_id)] = [str(d.tag_id)]
        except:
            pass
        finally:
            return result
