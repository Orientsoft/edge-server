# -*- coding: utf-8 -*-

from flask_script import Manager
from app import app, db

manager = Manager(app)


@manager.command
def init():
    from models.node import Node, ArchClass, NodesHasTag, NodesHasTask
    from models.service import Service, ServicesHasTag
    from models.tag import Tag
    from models.task import Task
    db.create_all(app=app)


if __name__ == "__main__":
    manager.run()
