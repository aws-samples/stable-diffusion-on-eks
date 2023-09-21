#!/bin/bash
source ~/.bashrc
cd $HOME/SageMaker/stable-diffusion-on-eks/
npm install
cdk bootstrap
cdk deploy --all --no-roll-back --require-approval never