# your_project/utils/env_loader.py

import os
from pathlib import Path

import environ


def load_env():
    base_dir = Path(__file__).resolve().parent.parent.parent  # Adjust as needed
    env_path = os.path.join(base_dir, '.env')
    env = environ.Env()
    environ.Env.read_env(env_path)
