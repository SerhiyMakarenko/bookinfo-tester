#!/bin/bash

# Check available resources
if [ `grep -c processor /proc/cpuinfo` -lt "4" ]; then
	echo "Minimum CPU number should be not less than 4, aborting!"
	exit 1
fi

if [ `grep MemTotal /proc/meminfo | awk '{print $2}'` -lt "8033440" ]; then
	echo "System should have not less than 8 Gb of RAM, aborting!"
	exit 1
fi

if [[ `df -k --output=avail "$PWD" | tail -n1` -lt 31457280 ]]; then
    echo "System should have not less than 30 Gb of free HDD, aborting!"
	exit 1
fi

# kubectl installation
apt-get update && sudo apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list
apt-get update
apt-get install -y kubectl=1.15.5-00

# KVM installation
apt-get install -y --no-install-recommends qemu-kvm libvirt-clients libvirt-daemon-system dnsmasq

# Installing onther software
sudo apt-get install -y git python3 python3-pip

# Create network minikube-net
virsh net-define minikube-net.xml
virsh net-autostart minikube-net
virsh net-start minikube-net

# minukube installation
cd /tmp/
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x/minikube
install minikube /usr/local/bin/

# Install helm
wget https://get.helm.sh/helm-v2.16.1-linux-amd64.tar.gz
tar -zxvf helm-v2.16.1-linux-amd64.tar.gz
install linux-amd64/helm /usr/local/bin/

# Add minikube user
useradd -p $(openssl passwd -1 minikube) minikube

# Setup permissions
adduser minikube libvirt
adduser minikube kvm
chown minikube /dev/kvm
