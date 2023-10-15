#!/bin/sh
mkdocs build -f ./docs/mkdocs.en.yml
mkdocs build -f ./docs/mkdocs.zh.yml
cp -av ./docs/index.html site/
cp -r site/* ../sd-on-eks-pages/
cd ../sd-on-eks-pages/
git add .
git commit -m "update doc"
git push