"""กติกา Python ร่วมกันระหว่างเกม Pygame และเว็บไซต์"""
import random
import emberfall_core as core

class Game:
    def __init__(self, job='1', seed=None):
        if job not in core.CLASSES:
            raise ValueError('อาชีพไม่ถูกต้อง')
        self.player=core.create_player(job)
        self.job=job; self.rng=random.Random(seed)
        self.region=0; self.stage=0; self.turn=1
        self.mode='route'; self.enemy=None
        self.logs=['เลือกเส้นทางเพื่อเริ่มการผจญภัย']
        self.effect=None

    def snapshot(self):
        return dict(player=self.player.copy(),job=self.job,region=self.region,stage=self.stage,
                    turn=self.turn,mode=self.mode,enemy=self.enemy.copy() if self.enemy else None,
                    logs=list(self.logs[-6:]),effect=self.effect,
                    region_name=core.REGIONS[self.region]['name'])

    def command(self, action):
        self.effect=None
        p=self.player
        if self.mode=='route':
            if action not in ('safe','treasure'):raise ValueError('เลือกเส้นทางก่อน')
            if action=='safe':self.logs.append(f'พักริมธาร ฟื้น {core.heal(p,10)} HP')
            else:
                d=min(self.rng.randint(5,11),p['hp']-1);p['hp']-=d;p['gold']+=18
                self.logs.append(f'พบสมบัติ +18 เหรียญ กับดัก −{d} HP')
            self.enemy=core.create_enemy(self.region,self.stage==2)
            self.turn=1;p['energy']=min(3,p['energy']+1);self.mode='battle'
            self.logs.append('พบ '+self.enemy['name'])
        elif self.mode=='battle':
            mapping={'attack':'1','skill':'2','guard':'3','potion':'4'}
            if action not in mapping:raise ValueError('คำสั่งต่อสู้ไม่ถูกต้อง')
            result=core.combat_turn(p,self.enemy,mapping[action],self.turn,self.rng)
            self.effect=dict(action=action,**result)
            self.logs.append(f"{'สกิล' if action=='skill' else 'โจมตี' if action=='attack' else 'ตั้งรับ' if action=='guard' else 'ดื่มยา'}: ทำดาเมจ {result['damage']} / ฟื้น {result['healed']} / รับ {result['received']}")
            if result['won']:
                reward=core.award_victory(p,self.enemy);self.stage+=1
                self.logs.append(f'ชนะ! ได้ {reward} เหรียญ')
                self.mode='victory' if self.region==2 and self.stage==3 else 'camp'
            elif p['hp']==0:self.mode='defeat'
            else:self.turn+=1
        elif self.mode=='camp':
            if action=='upgrade':core.upgrade(p);self.logs.append('ตีบวกอาวุธ ATK +5')
            elif action=='buy':core.buy_potion(p);self.logs.append('ซื้อยาฟื้นพลัง +1')
            elif action=='continue':
                amount=core.heal(p,round(p['max_hp']*.32));p['energy']=3
                self.logs.append(f'พักฟื้น {amount} HP และพลังสกิลเต็ม')
                if self.stage==3:self.region+=1;self.stage=0
                self.mode='route';self.enemy=None
            else:raise ValueError('เลือกคำสั่งที่กองไฟ')
        else:raise ValueError('เกมจบแล้ว เริ่มเกมใหม่ได้')
        return self.snapshot()
