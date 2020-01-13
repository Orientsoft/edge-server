# -*- coding: utf-8 -*-
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from applications.tag_manage import TagAction
from applications.service_manage import ServiceAction, ServiceNodeAction
from applications.task_manage import TaskAction, TaskDetailAction
from applications.nodeArch import ArchAction
from applications.nodes import NodeAction, NodeDeployLink
from applications.node_tag import NodeTagAction, TagNodeAction

from kubernetes import config, client

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
api = Api(app)

if app.config['IN_CLUSTER']:
    config.load_incluster_config()
else:
    config.load_kube_config()
api_instance = client.CoreV1Api()
custom_instance = client.CustomObjectsApi()
k8s_apps_v1 = client.AppsV1Api()

api.add_resource(TagAction, '/tag')
api.add_resource(TagNodeAction, '/tag/node')
api.add_resource(ServiceAction, '/service')
api.add_resource(ServiceNodeAction, '/service/node/<service_id>')
api.add_resource(TaskAction, '/task')
api.add_resource(TaskDetailAction, '/task/<task_id>')
api.add_resource(ArchAction, '/arch')
api.add_resource(NodeAction, '/node')
api.add_resource(NodeTagAction, '/node/tag')
api.add_resource(NodeDeployLink, '/deploy')


@app.route('/static/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/test/<name>', methods=['GET'])
def test(name):
    from applications.common.k8s import create_node, create_device_model, get_node_status, \
        list_node_status
    list_node_status()
    return ''


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'],
            threaded=True)
