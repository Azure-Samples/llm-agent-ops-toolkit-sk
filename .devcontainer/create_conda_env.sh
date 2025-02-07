#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda config --append channels conda-forge
conda create -n experimentation python=3.12 -y
conda activate experimentation && pip install -r experimentation/requirements_exp.txt
conda create -n evaluation python=3.12 -y
conda activate evaluation && pip install -r evaluation/requirements_eval.txt
conda activate base && pip install -r requirements.txt