# coding: utf-8
from app import db

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.INTEGER, primary_key=True)
    services_id = db.Column(db.ForeignKey('services.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                            index=True)
    name = db.Column(db.String(45))
    running = db.Column(db.Boolean)
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)
    token = db.Column(db.String(200))

    services = db.relationship('Service')
