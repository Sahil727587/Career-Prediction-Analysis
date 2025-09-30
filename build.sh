#!/usr/bin/env bash

# 1. Install all dependencies
pip install -r requirements.txt

# 2. Run the training script to generate the model assets (.pkl files)
python train_model.py