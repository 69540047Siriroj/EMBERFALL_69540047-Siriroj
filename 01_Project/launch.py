import sys, subprocess, os, venv
from pathlib import Path
root=Path(__file__).resolve().parent
os.chdir(root)
mode=sys.argv[1] if len(sys.argv)>1 else 'web'
if mode=='web':raise SystemExit(subprocess.call([sys.executable,'-X','utf8',str(root/'web_server.py')]))
env=root/'.venv';python=env/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
if not python.exists():
 print('Preparing game environment. Please wait...',flush=True);venv.create(env,with_pip=True)
if subprocess.run([str(python),'-c','import pygame'],capture_output=True).returncode:
 print('Installing pygame-ce. Internet required on first run.',flush=True)
 if subprocess.call([str(python),'-m','pip','install','pygame-ce==2.5.8']):raise SystemExit('Installation failed. Check internet and retry.')
raise SystemExit(subprocess.call([str(python),'-X','utf8',str(root/'desktop_game.py')]))
