import json, threading, unittest, urllib.request, urllib.error
from engine import Game
from web_server import Handler, ThreadingHTTPServer
class Tests(unittest.TestCase):
 def test_full_adventures(self):
  for job in ('1','2','3'):
   for seed in range(30):
    g=Game(job,seed);steps=0
    while g.mode not in ('victory','defeat'):
     p=g.player
     if g.mode=='route':a='safe'
     elif g.mode=='camp':a='upgrade' if p['gold']>=35+p['upgrades']*15 else 'buy' if p['gold']>=20 and p['potions']<3 else 'continue'
     else:a='guard' if g.turn%3==0 else 'potion' if p['hp']<=p['max_hp']*.5 and p['potions'] else 'skill' if p['energy']>=2 else 'attack'
     g.command(a);steps+=1;self.assertLess(steps,250)
    self.assertEqual(g.mode,'victory');self.assertEqual(g.player['wins'],9)
 def test_http_api(self):
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
  base='http://127.0.0.1:'+str(server.server_port)
  def post(path,data):
   req=urllib.request.Request(base+path,json.dumps(data).encode(),{'Content-Type':'application/json'})
   with urllib.request.urlopen(req) as r:return json.load(r)
  try:
   with urllib.request.urlopen(base) as r:self.assertIn(b'PYTHON WEB EDITION',r.read())
   with urllib.request.urlopen(base+'/assets/hero1.png') as r:self.assertTrue(r.read().startswith(b'\x89PNG'))
   r=post('/api/new',{'job':'1'});token=r['token'];self.assertEqual(r['state']['mode'],'route')
   r=post('/api/action',{'token':token,'action':'safe'});self.assertEqual(r['state']['mode'],'battle')
   r=post('/api/action',{'token':token,'action':'attack'});self.assertGreater(r['state']['effect']['damage'],0)
   self.assertEqual(post('/api/state',{'token':token})['state']['turn'],2)
   with self.assertRaises(urllib.error.HTTPError):post('/api/action',{'token':'invalid','action':'attack'})
   with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(base+'/engine.py')
  finally:server.shutdown();server.server_close()
if __name__=='__main__':unittest.main(verbosity=2)
