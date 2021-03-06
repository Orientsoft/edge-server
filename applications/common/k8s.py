# -*- coding: utf-8 -*-
from app import api_instance, custom_instance, k8s_apps_v1, app
import random, string

num = string.ascii_letters + string.digits


# 新建node时调用
def create_node(name):
    body = {
        "kind": "Node",
        "apiVersion": "v1",
        "metadata": {
            "name": name,
            "labels": {
                "name": "edge-node",
                "node-role.kubernetes.io/edge": ""
            }
        }
    }
    try:
        api_instance.create_node(body, pretty='true')
        return True
    except Exception as e:
        print(e)
        return False


def delete_node(name):
    try:
        api_instance.delete_node(name, async_req=True)
        return True
    except Exception as e:
        print(e)
        return False


# post services
def create_device_model(name):
    # body 由创建service提供，格式为json
    body = {'apiVersion': 'devices.kubeedge.io/v1alpha1',
            'kind': 'DeviceModel',
            'metadata': {'name': name, 'namespace': 'default'},
            'spec':
                {'properties':
                     [{'name': 'payload',
                       'description': 'payload type is json string ',
                       'type': {
                           'string': {'accessMode': 'ReadWrite', 'defaultValue': '{}'}
                       }
                       }]
                 }
            }
    try:
        custom_instance.create_namespaced_custom_object(group="devices.kubeedge.io",
                                                        version="v1alpha1",
                                                        namespace="default",
                                                        plural="devicemodels",
                                                        body=body
                                                        )
        return True
    except Exception as e:
        print(e)
        return False


class CreateDevice:
    def __init__(self, devicemodel):
        # service的参数
        self.deviceModelRef = devicemodel

    def deploy(self, node):
        # node 为节点的名字
        devicename = '{}-{}-{}'.format(self.deviceModelRef, node, "".join(random.sample(num, 6)).lower())
        body = {'apiVersion': 'devices.kubeedge.io/v1alpha1',
                'kind': 'Device',
                'metadata':
                    {'name': devicename,
                     'labels': {'description': self.deviceModelRef, 'model': self.deviceModelRef}},
                'spec':
                    {'deviceModelRef': {'name': self.deviceModelRef},
                     'nodeSelector': {'nodeSelectorTerms': [
                         {'matchExpressions': [{'key': '', 'operator': 'In', 'values': [node]}]}]}},
                'status':
                    {'twins': [{
                        'propertyName': 'payload',
                        'desired': {'metadata': {'type': 'string'}, 'value': 'e30K'}
                    }]
                    }
                }
        try:
            custom_instance.create_namespaced_custom_object(group="devices.kubeedge.io",
                                                            version="v1alpha1",
                                                            namespace="default",
                                                            plural="devices",
                                                            body=body
                                                            )
            return True, devicename
        except Exception as e:
            print(e)
            return False, ''


def delete_device(devicename):
    try:
        custom_instance.delete_namespaced_custom_object(
            group="devices.kubeedge.io",
            version="v1alpha1",
            namespace="default",
            plural="devices",
            name=devicename,
            body={}
        )
        return True
    except Exception as e:
        print(e)
        return False


class CreateDeploy:
    def __init__(self, kubernetes, image):
        self.kubernetes = kubernetes  # service.kubernetes
        self.image = image  # service.image

    # node_has_task.devicename
    def apply(self, devicename, nodename):
        env = self.kubernetes['env'] if 'env' in self.kubernetes else []
        volumeMounts = self.kubernetes['volumeMounts'] if 'volumeMounts' in self.kubernetes else []
        volumes = self.kubernetes['volumes'] if 'volumes' in self.kubernetes else []
        env.append({
            'name': 'DEVICE_ID', 'value': devicename
        })
        body = {'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {'name': devicename, 'namespace': 'default'},
                'spec':
                    {'replicas': 1,
                     'selector': {'matchLabels': {'name': 'edge-node'}},
                     'template':
                         {'metadata': {'labels': {'name': 'edge-node'}},
                          'spec':
                              {'nodeName': nodename,
                               'hostNetwork': True,
                               'containers':
                                   [{'name': devicename,
                                     'image': self.image,
                                     'volumeMounts': volumeMounts,
                                     'env': env,
                                     'securityContext': {'privileged': True}}],
                               'imagePullSecrets': [{'name': app.config['IMAGE_PULL_SECRET']}],
                               'tolerations': [
                                   {'effect': 'NoExecute', 'key': 'node.kubernetes.io/not-ready', 'operator': 'Exists',
                                    'tolerationSeconds': 86400},
                                   {'effect': 'NoExecute', 'key': 'node.kubernetes.io/unreachable',
                                    'operator': 'Exists',
                                    'tolerationSeconds': 86400}],
                               'volumes': volumes
                               }}}}
        try:
            k8s_apps_v1.create_namespaced_deployment(
                namespace="default",
                body=body
            )
            return True
        except Exception as e:
            print(e)
            return False


def delete_deploy(name):
    try:
        k8s_apps_v1.delete_namespaced_deployment(name=name, namespace='default')
        return True
    except Exception as e:
        return False


class CreatePod:
    def __init__(self, kubernetes, image):
        self.kubernetes = kubernetes  # service.kubernetes
        self.image = image  # service.image

    # node_has_task.devicename = podName
    def apply(self, devicename, nodename):
        env = self.kubernetes['env'] if 'env' in self.kubernetes else []
        volumeMounts = self.kubernetes['volumeMounts'] if 'volumeMounts' in self.kubernetes else []
        volumes = self.kubernetes['volumes'] if 'volumes' in self.kubernetes else []
        env.append({
            'name': 'DEVICE_ID', 'value': devicename
        })
        body = {'apiVersion': 'v1',
                'kind': 'Pod',
                'metadata': {'name': devicename, 'namespace': 'default'},
                'spec': {'nodeName': nodename,
                         'hostNetwork': True,
                         'containers':
                             [{'name': devicename,
                               'image': self.image,
                               'volumeMounts': volumeMounts,
                               'env': env,
                               'securityContext': {'privileged': True}}],
                         'imagePullSecrets': [{'name': app.config['IMAGE_PULL_SECRET']}],
                         'tolerations': [
                             {'effect': 'NoExecute', 'key': 'node.kubernetes.io/not-ready', 'operator': 'Exists',
                              'tolerationSeconds': 86400},
                             {'effect': 'NoExecute', 'key': 'node.kubernetes.io/unreachable',
                              'operator': 'Exists',
                              'tolerationSeconds': 86400}],
                         'volumes': volumes
                         }}
        print(body)
        try:
            api_instance.create_namespaced_pod(
                namespace="default",
                body=body
            )
            return True
        except Exception as e:
            print(e)
            return False


def delete_pod(name):
    try:
        api_instance.delete_namespaced_pod(
            name=name,
            namespace="default",
            async_req=False
        )
        # result = thread.get()
        # print(result)
        return True
    except:
        print('k8s client error')
        return False


def get_pod_exist(name):
    try:
        resp = api_instance.read_namespaced_pod(name=name, namespace="default")
        print(resp)
        if resp.status:
            return True
        else:
            return False
    except:
        print('k8s client error')
        return False


def get_node_status(name):
    try:
        resp = api_instance.read_node(name)
        if resp.status.conditions[-1].status == 'True':
            return True
        else:
            return False
    except:
        print('k8s client error')
        return False


def list_node_status():
    try:
        resp = api_instance.list_node()
        return_dict = {}
        # items.status.conditions.status
        for x in resp.items:
            return_dict[x.metadata.name] = True if x.status.conditions[-1].status == 'True' else False
        return return_dict
    except:
        pass


def update_node_online_status():
    from models.node import Node
    from app import db
    try:
        node_status_list = list_node_status()
        if not node_status_list:
            return False
        node_list = Node.query.all()
        for n in node_list:
            n.online = node_status_list.get(n.name, False)
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        db.session.rollback()
        return False
