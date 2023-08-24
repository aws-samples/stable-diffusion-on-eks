#! /bin/bash
aws ecr-public get-login-password --region us-east-1 | helm registry login public.ecr.aws -u AWS --password-stdin
helm package src/eks_cluster/charts/sd-on-eks
helm push sd-on-eks-0.1.0.tgz oci://public.ecr.aws/bingjiao/charts/
rm sd-on-eks-0.1.0.tgz