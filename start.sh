#!/usr/bin/env bash

# 1. Train model and create .pkl assets
python train_model.py

# 2. Launch the Gunicorn server for the Flask app
gunicorn app:app --bind 0.0.0.0:$PORT