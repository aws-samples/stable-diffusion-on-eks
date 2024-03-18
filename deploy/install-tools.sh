#!/bin/bash

set -e

kubectl_version='1.29.0'
helm_version='3.10.1'
yq_version='4.30.4'
s5cmd_version='2.2.2'
node_version='20.11.1'
cdk_version='2.115.0'

download () {
  url=$1
  out_file=$2
  curl --location --show-error --silent --output "$out_file" "$url"
}
cur_dir=$(pwd)
tmp_dir=$(mktemp -d)

cd "$tmp_dir"

if which pacapt > /dev/null
  then
    printf "\n"
  else
    sudo wget -O /usr/bin/pacapt https://github.com/icy/pacapt/raw/ng/pacapt
    sudo chmod 755 /usr/bin/pacapt
fi

sudo pacapt install --noconfirm jq git wget unzip openssl bash-completion python3 python3-pip

pip3 install -q awscurl==0.28 urllib3==1.26.6

# kubectl
if which kubectl > /dev/null
  then
    printf "kubectl is installed, skipping...\n"
  else
    printf "Installing kubectl...\n"
    download "https://dl.k8s.io/release/v$kubectl_version/bin/linux/amd64/kubectl" "kubectl"
    chmod +x ./kubectl
    sudo mv ./kubectl /usr/bin
fi

# helm
if which helm > /dev/null
  then
    printf "helm is installed, skipping...\n"
  else
    printf "Installing helm...\n"
    download "https://get.helm.sh/helm-v$helm_version-linux-amd64.tar.gz" "helm.tar.gz"
    tar zxf helm.tar.gz
    chmod +x linux-amd64/helm
    sudo mv ./linux-amd64/helm /usr/bin
    rm -rf linux-amd64/ helm.tar.gz
fi

# aws cli v2
printf "Installing/Upgrading AWS CLI v2...\n"
curl --location --show-error --silent "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -o -q awscliv2.zip -d /tmp
sudo /tmp/aws/install --update
rm -rf /tmp/aws awscliv2.zip

# yq
if which yq > /dev/null
  then
    printf "yq is installed, skipping...\n"
  else
    printf "Installing yq...\n"
    download "https://github.com/mikefarah/yq/releases/download/v${yq_version}/yq_linux_amd64" "yq"
    chmod +x ./yq
    sudo mv ./yq /usr/bin
fi

# s5cmd
if which s5cmd > /dev/null
  then
    printf "s5cmd is installed, skipping...\n"
  else
    printf "Installing s5cmd...\n"
    download "https://github.com/peak/s5cmd/releases/download/v${s5cmd_version}/s5cmd_${s5cmd_version}_Linux-64bit.tar.gz" "s5cmd.tar.gz"
    tar zxf s5cmd.tar.gz
    chmod +x ./s5cmd
    sudo mv ./s5cmd /usr/bin
    rm -rf s5cmd.tar.gz
fi

# Node.js
if which node > /dev/null
  then
    printf "Node.js is installed, skipping...\n"
  else
    printf "Installing Node.js...\n"
    download "https://nodejs.org/dist/v{$node_version}/node-v{$node_version}-linux-x64.tar.xz" "node.tar.xz"
    sudo mkdir -p /usr/local/lib/nodejs
    sudo tar -xJf node.tar.xz -C /usr/local/lib/nodejs
    export PATH="/usr/local/lib/nodejs/node-$node_version-linux-x64/bin:$PATH"
    printf "export PATH=\"/usr/local/lib/nodejs/node-$node_version-linux-x64/bin:\$PATH\"" >> ~/.bash_profile
    source ~/.bash_profile
fi

# CDK CLI
if which cdk > /dev/null
  then
    printf "CDK CLI is installed, skipping...\n"
  else
    printf "Installing AWS CDK CLI and bootstraping CDK environment...\n"
    sudo npm install -g aws-cdk@$cdk_version
fi

printf "Tools install complete. \n"

cd $cur_dir
rm -rf $tmp_dir
