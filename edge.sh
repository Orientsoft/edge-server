#!/usr/bin/env bash
set -e
package_address='address_for_replace'
package_name='package_for_replace'
crt_address='crt_for_replace'
key_address='key_for_replace'
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
    curl -sSL https://get.docker.com | sh
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
            exit 0
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

download_package(){
    wget $package_address -O $package_name
    tar -xvf $package_name
    cd $package_name/edge/conf
    wget $yaml_address -O edge.yaml
    # replace edge.yaml
    sed -i -e 's/{websocket_url_for_change}/'$socket_config'/g' edge.yaml
    sed -i -e 's/{node_id_for_change}/'$node_id_config'/g' edge.yaml
    sed -i -e 's/{interface_for_change}/'$interface_config'/g' edge.yaml
    sed -i -e 's/{podsandboximage_for_change}/'$image_config'/g' edge.yaml
    cd ../../
    $sh_c 'mv edge/ /etc/kubeedge/edge/'
}

download_cert(){
    wget $crt_address -O edge.crt
    wget $key_address -O edge.key
    $sh_c 'mkdir -p /etc/kubeedge/certs'
    $sh_c 'mv edge.crt /etc/kubeedge/certs/edge.crt'
    $sh_c 'mv edge.key /etc/kubeedge/certs/edge.key'
}

system_service(){
    $sh_c 'rm /etc/systemd/system/edgecore.service'
    $sh_c 'echo "[Unit]\nDescription=edgecore.service\n[Service]\nType=simple\nExecStart=/etc/kubeedge/edge/edgecore\n[Install]\nWantedBy=multi-user.target" >> /etc/systemd/system/edgecore.service'
    $sh_c 'systemctl daemon-reload'
    $sh_c 'systemctl start edgecore'
    $sh_c 'systemctl enable edgecore'
}

do_install() {
    get_distribution
    check_root
    install_docker
    export_env
    download_cert
    download_package
    system_service
    exit 1
}
do_install

