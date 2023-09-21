#!/bin/bash
cd $HOME
source ~/.bashrc
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 16
npm install -g aws-cdk
curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.27.1/2023-04-19/bin/linux/amd64/kubectl
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh
chmod +x ./kubectl
sudo cp ./kubectl /usr/local/bin
echo "Use bash shell via Terminal"

