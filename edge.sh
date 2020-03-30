#!/usr/bin/env bash
set -e
package_address='address_for_replace'
crt_address='crt_for_replace'
key_address='key_for_replace'
ca_address='ca_for_replace'
yaml_address='yaml_for_replace'
socket_config='socket_for_replace'
node_id_config='node_id_for_replace'
interface_config='interface_for_replace'
image_config='image_for_replace'


user="$(id -un 2>/dev/null || true)"
command_exists() {
	command -v "$@" > /dev/null 2>&1
}
sh_c='sh -c'
check_root(){
    if [ "$user" != 'root' ]; then
        if command_exists sudo; then
            sh_c='sudo -E sh -c'
        elif command_exists su; then
            sh_c='su -c'
        else
            echo "Error: this installer needs the ability to run commands as root.We are unable to find either "sudo" or "su" available to make this happen."
            exit 1
        fi
    fi
}
# install docker
install_docker(){
    curl -sSL https://get.daocloud.io/docker | sh
}
# check_os
get_distribution() {
	lsb_dist=""
	# Every system that we officially support has /etc/os-release
	if [ -r /etc/os-release ]; then
		lsb_dist="$(. /etc/os-release && echo "$ID")"
	fi
	# Returning an empty string here should be alright since the
	# case statements don't act unless you provide an actual value
	echo "$lsb_dist"
    lsb_dist="$(echo "$lsb_dist" | tr '[:upper:]' '[:lower:]')"
    case "$lsb_dist" in
        ubuntu|debian|raspbian)
            echo "$lsb_dist"
            ;;
        *)
            echo
            echo "ERROR: Unsupported distribution '$lsb_dist'"
            echo
            exit 1
            ;;
    esac
}

export_env(){
    $sh_c 'echo export DISPLAY=:0 >> /etc/profile'
    $sh_c 'echo xhost + >> /etc/profile'
}

create_dir(){
    $sh_c 'mkdir -p /etc/kubeedge/certs'
    $sh_c 'mkdir -p /etc/kubeedge/ca'
    $sh_c 'mkdir -p /etc/kubeedge/config'
    $sh_c 'mkdir -p /etc/kubeedge/edge'
}

download_cert(){
    wget $crt_address -O edge.crt
    wget $key_address -O edge.key
    wget $ca_address -O rootCA.crt
    $sh_c 'mv edge.crt /etc/kubeedge/certs/edge.crt'
    $sh_c 'mv edge.key /etc/kubeedge/certs/edge.key'
    $sh_c 'mv rootCA.crt /etc/kubeedge/ca/rootCA.crt'
}

download_config(){
    wget $yaml_address -O edgecore.yaml
    # replace edge.yaml
    sed -i -e 's/{websocket_url_for_change}/'$socket_config'/g' edgecore.yaml
    sed -i -e 's/{node_id_for_change}/'$node_id_config'/g' edgecore.yaml
    sed -i -e 's/{podsandboximage_for_change}/'$image_config'/g' edgecore.yaml
    #get interface
    ifaces=`ls /sys/class/net`
    echo $ifaces
    temp=true
    while $temp
    do
        read -p "chosse interface:>" -t 100 iface
        for i in $ifaces
            do
                if [ "${i}" = "$iface" ] ;then
                    temp=false
                    break
                fi
            done
        if [ "$temp" = true ];then
            echo 'please choose correct interface:'
        fi
    done
    ip="$(ip addr show "$iface"|grep "inet\b"|awk '{print $2}'|cut -d "/" -f1)"
    echo $ip

    sed -i -e 's/{interface_for_change}/'$iface'/g' edgecore.yaml
    sed -i -e 's/{ip_for_change}/'$ip'/g' edgecore.yaml

    $sh_c 'mv edgecore.yaml /etc/kubeedge/config/edgecore.yaml'
}

download_package(){
    wget $package_address -O edgecore
    chmod 777 edgecore
    $sh_c 'mv edgecore /etc/kubeedge/edge/edgecore'
}

system_service(){
    $sh_c 'rm -rf /etc/systemd/system/edgecore.service'
    $sh_c 'echo "[Unit]\nDescription=edgecore.service\n[Service]\nType=simple\nExecStart=/etc/kubeedge/edge/edgecore\nExecReload=/bin/kill -s HUP $MAINPID\nTimeoutSec=0\nRestartSec=2\nRestart=always\n[Install]\nWantedBy=multi-user.target" >> /etc/systemd/system/edgecore.service'
    $sh_c 'systemctl daemon-reload'
    $sh_c 'systemctl start edgecore'
    $sh_c 'systemctl enable edgecore'
}

do_install() {
    get_distribution
    check_root
    install_docker
    export_env
    create_dir
    download_cert
    download_config
    download_package
    system_service
    exit 1
}
do_install

