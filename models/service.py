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

    tags = db.relationship('Tag', secondary='services_has_tag')


class ServicesHasTag(db.Model):
    __tablename__ = 'services_has_tag'

    services_id = db.Column(db.ForeignKey('services.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                            index=True)
    tag_id = db.Column(db.ForeignKey('tag.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    id = db.Column(db.INTEGER, primary_key=True)

    services = db.relationship('Service')
    tag = db.relationship('Tag')

