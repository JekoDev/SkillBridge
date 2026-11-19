"""Opt-in OS app roots; discovery never executes applications."""
import os
import sys
from pathlib import Path
from .autodiscovery import connect

def system_roots():
    home = Path.home()
    if sys.platform == 'win32':
        candidates = [Path(os.environ[k]) for k in ('LOCALAPPDATA','APPDATA','PROGRAMFILES') if os.environ.get(k)]
    elif sys.platform == 'darwin':
        candidates = [Path('/Applications'), home/'Applications']
    else:
        candidates = [home/'.local/share', Path('/opt'), Path('/usr/local/share')]
    return [str(p) for p in candidates if p.is_dir()]

def connect_system(name):
    return connect(name, system_roots(), max_depth=2)
