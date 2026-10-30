"""เว็บไซต์ทำงานบนเครื่อง: python web_server.py ไม่ต้องติดตั้งแพ็กเกจเพิ่ม"""
import json, secrets, threading, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
from engine import Game
ROOT=Path(__file__).resolve().parent
SESSIONS={};LOCK=threading.Lock()
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def do_GET(self):
  path=urlsplit(self.path).path
  if path=='/':self.path='/web/index.html'
  elif not path.startswith(('/web/','/assets/')):
   self.send_error(404);return
  super().do_GET()
 def do_POST(self):
  if self.headers.get('Origin') not in (None,'http://'+self.headers.get('Host','')):
   self.send_error(403);return
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<2048:raise ValueError('ข้อมูลไม่ถูกต้อง')
   data=json.loads(self.rfile.read(size));path=urlsplit(self.path).path
   with LOCK:
    if path=='/api/new':
     if len(SESSIONS)>=100:raise ValueError('เซสชันเต็ม กรุณาปิดแล้วเปิดเซิร์ฟเวอร์ใหม่')
     token=secrets.token_hex(16);game=Game(data.get('job','1'));SESSIONS[token]=game
    else:
     token=data.get('token','');game=SESSIONS.get(token)
     if not game:raise ValueError('ไม่พบเกม กดเริ่มเกมใหม่')
     if path=='/api/action':game.command(data.get('action',''))
     elif path!='/api/state':raise ValueError('ไม่พบคำสั่ง')
    self.reply(200,dict(token=token,state=game.snapshot()))
  except (ValueError,KeyError,TypeError) as e:self.reply(400,dict(error=str(e)))
 def reply(self,status,value):
  raw=json.dumps(value,ensure_ascii=False).encode();self.send_response(status)
  self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def log_message(self,*args):pass
if __name__=='__main__':
 server=None
 for port in range(8765,8785):
  try:server=ThreadingHTTPServer(('127.0.0.1',port),Handler);break
  except OSError:continue
 if server is None:raise SystemExit('ไม่พบพอร์ตว่าง กรุณาปิดเกมที่เปิดค้างไว้')
 url=f'http://127.0.0.1:{server.server_port}'
 print('EMBERFALL Python Web Game:',url,'\nKeep this window open. Ctrl+C to stop.')
 threading.Timer(.8,lambda:webbrowser.open(url)).start()
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
