#!/bin/bash
source ~/.bashrc
cd $HOME/SageMaker/SDonEKS-Deploy/stable-diffusion-on-eks/
npm install
cdk bootstrap
cdk deploy --all --no-roll-back