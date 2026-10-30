"""Pygame: python desktop_game.py (ภาพวาด pixel art อยู่ใน assets)"""
import os, sys, math, time
from pathlib import Path
if '--selftest' in sys.argv:os.environ['SDL_VIDEODRIVER']='dummy'
import pygame
from engine import Game

ROOT=Path(__file__).resolve().parent
pygame.init()
W,H=1000,720
screen=pygame.display.set_mode((W,H));pygame.display.set_caption('EMBERFALL | Python + Pygame')
clock=pygame.time.Clock();font=pygame.font.Font(None,25);small=pygame.font.Font(None,21);large=pygame.font.Font(None,44)
INK=(235,232,212);GOLD=(225,180,111);MUTED=(159,181,172)
images={p.stem:pygame.image.load(str(p)).convert_alpha() for p in (ROOT/'assets').glob('*.png')}
game=None;buttons=[];effect_at=0;message='Choose your hero. Every third enemy turn is a heavy attack.'

def text(s,x,y,color=INK,big=False):screen.blit((large if big else font).render(str(s),True,color),(x,y))
def button(rect,label,action,enabled=True):
 r=pygame.Rect(rect);pygame.draw.rect(screen,(40,59,56) if enabled else (25,35,34),r,border_radius=8)
 pygame.draw.rect(screen,GOLD if enabled else (55,65,61),r,1,border_radius=8)
 screen.blit(small.render(label,True,INK if enabled else MUTED),(r.x+12,r.y+15));buttons.append((r,action,enabled))

def render():
 global buttons
 buttons=[];screen.fill((15,25,26));text('EMBERFALL',34,22,GOLD,True);text('Python adventure | Mouse controls',650,35,MUTED)
 if game is None:
  text('THE LAST FLAME',330,95,GOLD,True)
  text('Cross three lands. Defeat the Ash King.',300,151)
  screen.blit(pygame.transform.scale(images['bg2'],(930,275)),(35,195))
  for i,(name,hp,atk) in enumerate([('KNIGHT',145,19),('MAGE',105,25),('RANGER',120,22)]):
   x=90+i*300;screen.blit(images[f'hero{i+1}'],(x+12,235))
   button((x,490,240,55),f'{name} | HP {hp} / ATK {atk}','new'+str(i+1))
  text('Attack, cast a skill, guard heavy attacks, and heal.',250,584,MUTED)
  text('Images and animations are rendered by Python + Pygame.',220,625,MUTED)
  button((390,655,220,45),'EXIT GAME','exit');return
 s=game.snapshot();p=s['player'];r=s['region'];mode=s['mode']
 text(['Whispering Woods','Moonlit Sanctum','Ashen Crown'][r],35,80,GOLD)
 text(f"Victories {p['wins']}/9 | HP {p['hp']}/{p['max_hp']} | ATK {p['atk']} | Gold {p['gold']} | Potions {p['potions']}",35,117)
 button((805,75,160,43),'NEW GAME','reset')
 screen.blit(pygame.transform.scale(images[f'bg{r}'],(930,345)),(35,160))
 elapsed=time.monotonic()-effect_at;effect=s['effect'];offset=0
 if effect and elapsed<.5 and effect['action'] in ('attack','skill'):offset=90*math.sin(elapsed/.5*math.pi)
 bob=int(3*math.sin(time.monotonic()*2.8))
 screen.blit(images[f'hero{s["job"]}'],(140+offset,245+bob))
 if s['enemy']:
  img=images[f'{"boss" if s["enemy"]["boss"] else "enemy"}{r}'];screen.blit(img,(625,213-bob))
  e=s['enemy'];pygame.draw.rect(screen,(66,41,44),(645,203,250,10));pygame.draw.rect(screen,(209,126,105),(645,203,int(250*e['hp']/e['max_hp']),10))
  text(('BOSS' if e['boss'] else 'ENEMY')+f" HP {e['hp']}/{e['max_hp']}",650,172)
 if effect and elapsed<.9:
  if effect['damage']:text('-'+str(effect['damage']),740,280-int(elapsed*70),GOLD,True)
  if effect['received']:text('-'+str(effect['received']),240,300-int(elapsed*60),(255,157,127),True)
  if effect['healed']:text('+'+str(effect['healed']),240,280-int(elapsed*60),(143,225,170),True)
  if effect['guarded']:pygame.draw.circle(screen,(145,201,214),(265,365),100,3)
  if effect['action']=='skill':
   for i in range(8):pygame.draw.circle(screen,GOLD,(int(720+90*math.cos(i+elapsed*10)),int(350+65*math.sin(i+elapsed*10))),5)
 text(f"Skill energy: {p['energy']}/3",50,477,GOLD)
 if mode=='battle':
  text(f"TURN {s['turn']} | "+('HEAVY ATTACK NEXT: GUARD!' if s['turn']%3==0 else 'Enemy prepares a normal attack'),45,526,GOLD)
  for i,(label,a,enabled) in enumerate([('ATTACK (+1 energy)','attack',True),('SKILL (2 energy)','skill',p['energy']>=2),('GUARD (-75% dmg)','guard',True),('POTION (+55 HP)','potion',p['potions']>0 and p['hp']<p['max_hp'])]):button((40+i*240,570,225,60),label,a,enabled)
 elif mode=='route':
  text('Choose a path. A battle awaits on either route.',45,526)
  button((80,570,390,60),'RIVER PATH | Heal 10 HP','safe');button((530,570,390,60),'TREASURE | +18 gold, lose 5-11 HP','treasure')
 elif mode=='camp':
  text('CAMPFIRE | Buy supplies, then rest and continue.',45,526,GOLD)
  cost=35+p['upgrades']*15
  button((40,570,285,60),f'UPGRADE +5 ATK | {cost} gold','upgrade',p['gold']>=cost)
  button((345,570,240,60),'POTION | 20 gold','buy',p['gold']>=20 and p['potions']<5)
  button((605,570,350,60),'REST +32% HP & CONTINUE','continue')
 else:
  text('VICTORY! YOU RESTORED THE FLAME.' if mode=='victory' else 'DEFEATED. A NEW JOURNEY AWAITS.',70,526,GOLD)
  button((180,570,290,60),'PLAY AGAIN','reset');button((530,570,290,60),'EXIT GAME','exit')
 text(message[:100],40,654,MUTED);text('ESC: back to hero selection | Close window: exit',40,685,MUTED)

if '--selftest' in sys.argv:
 game=Game('1',1);render();pygame.image.save(screen,str(ROOT/'Desktop_Preview.png'))
 game.command('safe');render();game.command('attack');effect_at=time.monotonic();render()
 pygame.image.save(screen,str(ROOT/'Desktop_Battle.png'))
 for m in ('camp','victory','defeat'):game.mode=m;render()
 print('PASS: Pygame renders route, battle, camp, victory and defeat');pygame.quit();sys.exit()

running=True
while running:
 render();pygame.display.flip()
 for event in pygame.event.get():
  if event.type==pygame.QUIT:running=False
  elif event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:game=None
  elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
   for rect,action,enabled in buttons:
    if enabled and rect.collidepoint(event.pos):
     if action=='exit':running=False
     elif action=='reset':game=None;message='Choose a hero to begin a new journey.'
     elif action.startswith('new'):game=Game(action[-1]);message='Choose a path to begin.'
     else:
      if time.monotonic()-effect_at<.45:break
      try:game.command(action);effect_at=time.monotonic();message='Action complete. Check HP and the next enemy intent.'
      except ValueError:message='Cannot use this action. Check your energy, gold, or potions.'
     break
 clock.tick(60)
pygame.quit()
