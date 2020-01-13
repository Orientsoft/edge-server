#!/usr/bin/env bash
wget "package_address" -O package_name
tar -xvf package_name
cd package_name/edge/conf
wget "yaml_address" -O edge.yaml
# 替换相应的内容
sed -i 's/{websocket_url_for_change}/socket_config/g' edge.yaml
sed -i 's/{node_id_for_change}/node_id_config/g' edge.yaml
sed -i 's/{interface_for_change}/interface_config/g' edge.yaml
sed -i 's/{podsandboximage_for_change}/image_config/g' edge.yaml
# 下载证书
wget "crt_address" -O edge.crt
wget "key_address" -O edge.key
mkdir -p /etc/kubeedge/certs
mv edge.crt /etc/kubeedge/certs/edge.crt
mv edge.key /etc/kubeedge/certs/edge.key
# cp 到/etc/kubeedge/
cd ../..
/bin/cp -rf * /etc/kubeedge/
# systemctl 配置
# start edgecore
cd /etc/kubeedge/edge/
nohup ./edgecore > edgecore.log &