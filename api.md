# API

## 一、用户管理

USER_ROLES:

```js
const USER_ROLES = {
    ADMIN: 0,
    SUPER: 1,
};
```

登录API需要防攻击：  
   1. 暴力搜索攻击：请求5次失败封IP 20秒  
   2. 爆库攻击：数据库存储密码的SHA256散列值  
   3. 抓包攻击：客户端对密码加盐加密：```公钥加密(SHA256(密码)@当前时间串)```；服务端：```rsplit(私钥解密(密文), '@')[0]```  

loginRequest:

```
{
    name: String,
    key: String, // 英文及数字8位以上，密文
}
```

userInRequest:

```js
{
    name: String,
    key: String, // 英文及数字8位以上，密文
    role: Number, // USER_ROLES
}
```

userInResponse:

```js
{
    id: Id,
    name: String,
    role: Number, // USER_ROLES
    createdAt: Date,
    updatedAt: Date,
    lastLogin: Date
}
```

| method | path | query | request | response | remark |
| ------ | ---- | ----- | ------- | -------- | ------ |
| GET | /users | name, role | | [ userInResponse ] | 用户列表 |
| POST | /users | | userInRequest | userInResponse | 创建用户 |
| GET | /users/:userId | | | userInResponse | 获取指定用户 |
| PUT | /users/:userId | | userInRequest | userInResponse | 替换指定用户 |
| PATCH | /users/:userId | | userInRequest | userInResponse | 更改指定用户 |
| DELETE | /users/:userId | | | | 删除指定用户 |
| POST | /login | | loginRequest | userInResponse | 用户登录 |
| GET | /logout | |  | | 用户登出 |

## 二、节点管理

### 2.1 分组

分组功能是用Tag实现的——允许给节点添加任意多个Tag，并允许以任意逻辑串进行Tag匹配。  

tagInRequest:

```
{
    name: String,
    type: String,
    ref: Id,
}
```

tagInResponse:

```
{
    id: Id,
    name: String,
    type: String,
    ref: Id,
}
```

| method | path | query | request | response | remark |
| ------ | ---- | ----- | ------- | -------- | ------ |
| GET | /tags | name, type, ref | | [ tagInResponse ] | Tag列表 |
| POST | /tags | | tagInRequest | tagInResponse | 创建Tag |
| GET | /tags/:tagId | | | tagInResponse | 获取指定Tag |
| PUT | /tags/:tagId | | tagInRequest | tagInResponse | 替换指定Tag |
| PATCH | /tags/:tagId | | tagInRequest | tagInResponse | 更改指定Tag |
| DELETE | /tags/:tagId | | | | 删除指定Tag |
   
### 2.2 认证

节点认证是节点用KubeEdge连接的时候，需要使用服务提供的公钥验证。  
edge-server提供生成公私钥文件的功能，并允许公钥文件下载。  
注意生成新密钥对会造成CloudHub重启，并且以前的公私钥文件**全部失效**。  
因此该功能主要为用户提供公钥下载链接，生成密钥需要超级管理员权限。  

| method | path | query | request | response | remark |
| ------ | ---- | ----- | ------- | -------- | ------ |
| GET | /certs | | | certInResponse | 下载公钥文件 |
| POST | /certs | | | | 生成密钥对 |

### 2.3 节点

允许给出一个tag列表来进行节点查询。  

NODE_ARCHS:

```js
const NODE_ARCHS = {
    x86: 10,
    x86-64: 11,
    armv7l: 20,
};
```

nodeInRequest:

```
{
    name: String,
    arch: NODE_ARCHS,
    core: Number,
    memory: Number,
    storage: Number,
    gpu: Boolean,
    parallel: Number,
    task: Number,
    online: Boolean,
}
```

nodeInResponse:

```
{
    id: Id,
    name: String,
    arch: NODE_ARCHS,
    core: Number,
    memory: Number,
    storage: Number,
    gpu: Boolean,
    parallel: Number,
    task: Number,
    online: Boolean,
    createdAt: Date,
    updatedAt: Date
}
```

| method | path | query | request | response | remark |
| ------ | ---- | ----- | ------- | -------- | ------ |
| GET | /nodes | name, arch, core, memory, storage, gpu, parallel, task, online, tags | | [ nodeInResponse ] | 节点列表 |
| POST | /nodes | | nodeInRequest | nodeInResponse | 创建节点 |
| GET | /nodes/:nodeId | | | nodeInResponse | 获取指定节点 |
| PUT | /nodes/:nodeId | | nodeInRequest | nodeInResponse | 替换指定节点 |
| PATCH | /nodes/:nodeId | | nodeInRequest | nodeInResponse | 更改指定节点 |
| DELETE | /nodes/:nodeId | | | | 删除指定节点 |

## 三、服务管理

serviceInRequest:

```
{
    name: String,
    description: String,
    image: String,
    requirement: String, // TODO: tag or k8s要求描述
}
```

serviceInResponse:

```
{
    id: Id,
    name: String,
    description: String,
    image: String,
    requirement: String, // TODO: tag or k8s要求描述
    createdAt: Date,
    updatedAt: Date
}
```

| method | path | query | request | response | remark |
| ------ | ---- | ----- | ------- | -------- | ------ |
| GET | /services | name, arch, image | | [ serviceInResponse ] | 服务列表 |
| POST | /services | | serviceInRequest | serviceInResponse | 创建服务 |
| GET | /services/:serviceId | | | serviceInResponse | 获取指定服务 |
| PUT | /services/:serviceId | | serviceInRequest | serviceInResponse | 替换指定服务 |
| PATCH | /services/:serviceId | | serviceInRequest | serviceInResponse | 更改指定服务 |
| DELETE | /services/:serviceId | | | | 删除指定服务 |

## 四、任务管理

需要实现简单的任务审计，统计实际执行该任务的节点/未执行的节点。  

taskInRequest:

```
{
    service: Id,
    nodes: [ Id ],
    running: Boolean,
}
```

taskInResponse:

```
{
    id: Id,
    service: Id,
    nodes: [ Id ],
    running: Boolean,
}
```

nodeStatusInResponse:

```
{
    node: Id,
    running: Boolean,
}
```

statusInResponse:

```
{
    task: Id,
    nodes: [ nodeStatusInResponse ]
}
```

| method | path | query | request | response | remark |
| ------ | ---- | ----- | ------- | -------- | ------ |
| GET | /tasks | service, nodes, running | | [ taskInResponse ] | 任务列表 |
| POST | /tasks | | taskInRequest | taskInResponse | 创建任务 |
| GET | /tasks/:taskId | | | taskInResponse | 获取指定任务 |
| PUT | /tasks/:taskId | | taskInRequest | taskInResponse | 替换指定任务 |
| PATCH | /tasks/:taskId | | taskInRequest | taskInResponse | 更改指定任务 |
| DELETE | /tasks/:taskId | | | | 删除指定任务 |
| GET | /tasks/start/:taskId/ | | | taskInResponse | 启动指定任务 |
| GET | /tasks/stop/:taskId/ | | | taskInResponse | 停止指定任务 |
| GET | /tasks/status/:taskId/ | | | statusInResponse | 获取指定任务状态 |
