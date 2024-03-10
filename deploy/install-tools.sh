#!/bin/bash

set -e

kubectl_version='1.29.0'
helm_version='3.10.1'
yq_version='4.30.4'
s5cmd_version='2.2.2'
node_version='20.1.1'
cdk_version='2.115.0'

download () {
  url=$1
  out_file=$2
  curl --location --show-error --silent --output "$out_file" "$url"
}
cur_dir=$(pwd)
tmp_dir=$(mktemp -d)

cd $tmp_dir

yum install --quiet -y findutils jq tar gzip zsh git diffutils wget \
  tree unzip openssl gettext bash-completion python3 pip3 python3-pip \
  amazon-linux-extras nc yum-utils

pip3 install -q awscurl==0.28 urllib3==1.26.6

# kubectl
printf "Installing kubectl..."
download "https://dl.k8s.io/release/v$kubectl_version/bin/linux/amd64/kubectl" "kubectl"
chmod +x ./kubectl
mv ./kubectl /usr/local/bin

# helm
printf "Installing helm..."
download "https://get.helm.sh/helm-v$helm_version-linux-amd64.tar.gz" "helm.tar.gz"
tar zxf helm.tar.gz
chmod +x linux-amd64/helm
mv ./linux-amd64/helm /usr/local/bin
rm -rf linux-amd64/ helm.tar.gz

# aws cli v2
printf "Installing AWS CLI v2..."
curl --location --show-error --silent "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -o -q awscliv2.zip -d /tmp
/tmp/aws/install --update
rm -rf /tmp/aws awscliv2.zip

# yq
printf "Installing yq..."
download "https://github.com/mikefarah/yq/releases/download/v${yq_version}/yq_linux_amd64" "yq"
chmod +x ./yq
mv ./yq /usr/local/bin

# s5cmd
printf "Installing s5cmd..."
download "https://github.com/peak/s5cmd/releases/download/s5cmd_${s5cmd_version}_Linux-64bit.tar.gz" "s5cmd.tar.gz"
tar zxf s5cmd.tar.gz
chmod +x ./s5cmd
mv ./s5cmd /usr/local/bin
rm -rf s5cmd.tar.gz

# Node.js
if which node > /dev/null
  then
      printf "Node.js is installed, skipping..."
  else
      printf "Installing Node.js..."
      download "https://nodejs.org/dist/v{$node_version}/node-v{$node_version}-linux-x64.tar.xz" "node.tar.xz"
      sudo mkdir -p /usr/local/lib/nodejs
      sudo tar -xJvf node.tar.xz -C /usr/local/lib/nodejs
      export PATH=/usr/local/lib/nodejs/node-$node_version-linux-x64/bin:$PATH
      printf "export /usr/local/lib/nodejs/node-$node_version-linux-x64/bin:\$PATH" >> ~/.bash_profile
      source ~/.bash_profile
  fi

# CDK CLI
printf "Installing AWS CDK CLI and bootstraping CDK environment..."
sudo npm install -g aws-cdk@$cdk_version
cdk bootstrap

printf "Tools install complete. "

cd $cur_dir