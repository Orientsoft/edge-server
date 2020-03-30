# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
# from ext import role_check
import datetime
import json


class TaskAction(Resource):
    # 新建任务 建device
    def post(self):
        from app import db
        from models.task import Task
        from models.node import NodesHasTask, NodesHasTag
        from models.service import Service
        from applications.common.k8s import CreateDevice
        from applications.common.token import encode_jwt
        services_id = request.json.get('service_id')
        node_ids = request.json.get('node_ids')
        name = request.json.get('name')
        # 需校验node节点的体系tag是否支持改service。node_result = {"1":"pi-4"}
        try:
            nodes, node_result = NodesHasTag.available_node(node_ids, services_id)
            if not nodes:
                return '请选择可用的节点', 400
            s = Service.query.get(services_id)
            if not s:
                return '服务不存在', 400
            t = Task()
            t.services_id = services_id
            t.name = name
            t.running = False
            t.createdAt = datetime.datetime.now()
            t.updatedAt = datetime.datetime.now()
            t.token = ''
            db.session.add(t)
            db.session.flush()
            t.token = encode_jwt({'task': t.id})
            c = CreateDevice(s.devicemodel)
            for r in nodes:
                status, device_name = c.deploy(node_result[str(r)])
                if status:
                    nht = NodesHasTask()
                    nht.nodes_id = r
                    nht.task_id = t.id
                    nht.device_name = device_name
                    db.session.add(nht)
                else:
                    db.session.rollback()
                    return '创建失败', 400
            db.session.commit()
            return 'success', 200
        except:
            db.session.rollback()
            return '创建失败', 400

    def get(self):
        from models.task import Task
        from applications.common.k8s import update_node_online_status
        try:
            update_node_online_status()
            running = request.args.get('running', None)
            services_id = request.args.get('service_id', None)
            dataObj = Task.query
            if running:
                dataObj = dataObj.filter_by(running=running)
            if services_id:
                dataObj = dataObj.filter_by(services_id)
            resultObj = dataObj.all()
            returnObj = []
            for r in resultObj:
                nodes = []
                for x in r.nodes:
                    tags = {}
                    buss_tags = []
                    for y in x.tags:
                        if y.type == '业务':
                            buss_tags.append({'id': y.id, 'name': y.name})
                        elif y.type == '体系':
                            tags = {'id': y.id, 'name': y.name}
                    nodes.append({'id': x.id, 'name': x.name, 'online': x.online, 'parallel': x.parallel,
                                  'arch': x.arch_class.name, 'tags': tags, 'buss_tags': buss_tags,
                                  'createdAt': x.createdAt.strftime('%Y-%m-%d %H:%M:%S')})
                returnObj.append({
                    "id": str(r.id),
                    "name": r.name,
                    "service_id": r.services_id,
                    "service_name": r.services.name,
                    "service_image": r.services.image,
                    "running": r.running,
                    "createdAt": r.createdAt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(r.createdAt,
                                                                                         datetime.datetime) else r.createdAt,
                    "updatedAt": r.updatedAt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(r.updatedAt,
                                                                                         datetime.datetime) else r.updatedAt,
                    "token": r.token,
                    "nodes": nodes
                })
            return returnObj
        except:
            return []

    def patch(self):
        from models.task import Task
        from models.node import NodesHasTag, NodesHasTask
        from applications.common.k8s import CreateDevice, delete_device
        from app import db
        try:
            taskid = request.json.get('id')
            # 任务创建后，不可变更服务，可追加节点
            node_ids = request.json.get('node_ids', None)
            name = request.json.get('name', None)
            task = Task.query.get(taskid)
            if not task:
                return '任务不存在', 400
            if task.running:
                return '此状态不允许修改，请先停止任务', 400
            if node_ids:
                nodes, node_result = NodesHasTag.available_node(node_ids, task.services_id)
                if not nodes:
                    return '请选择可用的节点', 400
                old_nodes = list(map(lambda x: str(x.id), task.nodes))
                need_delete = list(set(old_nodes) - set(nodes))
                need_add = list(set(nodes) - set(old_nodes))
                c = CreateDevice(task.services.devicemodel)
                # 新增节点
                for n in need_add:
                    # 新增device
                    status, device_name = c.deploy(node_result[str(n)])
                    if status:
                        nht = NodesHasTask()
                        nht.task_id = task.id
                        nht.nodes_id = n
                        nht.device_name = device_name
                        db.session.add(nht)
                # 删除节点
                temp = NodesHasTask.query.filter(NodesHasTask.task_id == task.id,
                                                 NodesHasTask.nodes_id.in_(need_delete)).all()
                for t in temp:
                    if delete_device(t.device_name):
                        db.session.delete(t)
            if name:
                task.name = name
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200

    # @role_check
    def delete(self):
        from models.task import Task
        from models.node import NodesHasTask
        from applications.common.k8s import delete_device
        from app import db
        try:
            id = request.json.get('id')
            t = Task.query.get(id)
            if t:
                if t.running:
                    return '此状态不允许删除', 400
                temp = NodesHasTask.query.filter(NodesHasTask.task_id == t.id).all()
                for d in temp:
                    if delete_device(d.device_name):
                        db.session.delete(d)
                db.session.delete(t)
                db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200


# 查询某一个任务的部署节点

class TaskDetailAction(Resource):
    def get(self, task_id):
        returnObj = {}
        returnObj['nodes'] = []
        from models.task import Task
        from models.node import NodesHasTask
        try:
            task = Task.query.get(task_id)
            if not task:
                return '任务不存在', 400
            dataObj = NodesHasTask.query.filter_by(task_id=task_id).all()
            for d in dataObj:
                returnObj['nodes'].append({
                    "node_id": d.nodes_id,
                    "device_name": d.device_name,
                    "node_name": d.nodes.name,
                    "node_arch": d.nodes.arch_class.name,
                    "node_parallel": d.nodes.parallel,
                    "node_online": d.nodes.online,
                    "node_createdAt": d.nodes.createdAt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(d.nodes.createdAt,
                                                                                                    datetime.datetime) else d.nodes.createdAt,
                })
            returnObj['task_id'] = task_id
            returnObj['task_running'] = task.running
            returnObj['task_name'] = task.name
            returnObj['task_token'] = task.token
            # returnObj['service'] = {"name": task.services.name, "description": task.services.description,
            #                         "image": task.services.image}
            return returnObj
        except:
            return {}

    def post(self, task_id):
        from models.task import Task
        from models.node import NodesHasTask
        from applications.common.k8s import CreateDeploy, delete_deploy, CreatePod, delete_pod, get_node_status, \
            get_pod_exist
        from app import db
        try:
            task = Task.query.get(task_id)
            if not task:
                return '任务不存在', 400
            operator = request.json.get('operator')  # start / stop
            baseObj = alldevice = NodesHasTask.query.filter_by(task_id=task_id).all()
            # 检查该task对应的node是否都在线
            for b in baseObj:
                if not get_node_status(b.nodes.name):
                    return '{}节点不在线'.format(b.nodes.name), 400
                pod_status = get_pod_exist(b.device_name)
                if operator == 'start' and pod_status:
                    return 'pod:{}已存在'.format(b.device_name), 400
            if operator == 'start':
                task.running = True
                kubernetes = json.loads(task.services.kubernetes)
                c = CreatePod(kubernetes, task.services.image)
                for a in alldevice:
                    if not c.apply(a.device_name, a.nodes.name):
                        return '启动失败', 400
            elif operator == 'stop':
                task.running = False
                for a in alldevice:
                    # 删除deployment
                    if not delete_pod(a.device_name):
                        return '停止失败', 400
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return 'ERROR', 500
        return 'success', 200
