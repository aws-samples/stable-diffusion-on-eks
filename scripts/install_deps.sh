#!/bin/bash

npm install

source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt