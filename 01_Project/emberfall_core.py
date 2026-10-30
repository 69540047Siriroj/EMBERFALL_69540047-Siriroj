"""EMBERFALL - เกม Python มาตรฐาน ไม่ต้องติดตั้งแพ็กเกจเพิ่ม
รัน: python emberfall.py | ปิดแอนิเมชัน: python emberfall.py --fast
"""
import random
import sys
import time

ANIMATION = True
CLASSES = {
    '1': dict(name='อัศวิน', hp=145, atk=19, skill='ดาบพิพากษา'),
    '2': dict(name='จอมเวท', hp=105, atk=25, skill='ดาวตกเพลิง'),
    '3': dict(name='นักธนู', hp=120, atk=22, skill='ศรทะลวง'),
}
REGIONS = [
    dict(name='ป่ากระซิบ', enemy='หมาป่าเงา', boss='ผู้พิทักษ์รากไม้'),
    dict(name='วิหารจันทรา', enemy='ผู้เฝ้าวิหาร', boss='อัศวินจันทราทมิฬ'),
    dict(name='ยอดเขาเถ้าถ่าน', enemy='อสูรเถ้าถ่าน', boss='มังกรราชันเถ้าถ่าน'),
]

class ExitGame(Exception):
    """ส่งสัญญาณออกจากเกมกลับไปยัง main โดยไม่แสดง traceback"""


def type_text(text, speed=0.012):
    if not ANIMATION:
        print(text)
        return
    for char in text:
        print(char, end='', flush=True)
        time.sleep(speed)
    print()


def loading(text):
    print(text, end='', flush=True)
    for _ in range(3):
        if ANIMATION:
            time.sleep(0.18)
        print(' .', end='', flush=True)
    print()


def attack_animation(name, damage, skill=False):
    type_text(f"{'✦' if skill else '⚔'} {name} {'รวบรวมพลัง' if skill else 'พุ่งเข้าโจมตี'}...")
    print(f"      {'✧ ━━━ ✦ ━━━ ✧' if skill else '─── ⚔ ──→'}  −{damage} HP")
    if ANIMATION:
        time.sleep(0.18)


def choose(prompt, options):
    while True:
        answer = input(prompt).strip()
        if answer.lower() in ('0', 'q', 'quit'):
            raise ExitGame()
        if answer in options:
            return answer
        print('ข้อมูลไม่ถูกต้อง เลือก ' + ', '.join(options) + ' หรือ 0 เพื่อออก')


def create_player(class_key, name='ผู้ถือเปลวไฟ'):
    job = CLASSES[class_key]
    return dict(name=name, job=job['name'], hp=job['hp'], max_hp=job['hp'],
                atk=job['atk'], skill=job['skill'], gold=30, potions=3,
                energy=2, upgrades=0, wins=0)


def heal(player, amount):
    before = player['hp']
    player['hp'] = min(player['max_hp'], before + amount)
    return player['hp'] - before


def show_status(p):
    blocks = round(20 * p['hp'] / p['max_hp'])
    print(f"\n{p['name']} | {p['job']}")
    print(f"HP [{'█' * blocks}{'░' * (20-blocks)}] {p['hp']}/{p['max_hp']}")
    print(f"ATK {p['atk']} | พลังสกิล {'◆' * p['energy']}{'◇' * (3-p['energy'])}")
    print(f"เหรียญ {p['gold']} | ยาฟื้นพลัง {p['potions']}/5")


def create_enemy(region_index, is_boss):
    region = REGIONS[region_index]
    hp = 125 + region_index * 75 if is_boss else 48 + region_index * 27
    return dict(name=region['boss'] if is_boss else region['enemy'],
                hp=hp, max_hp=hp, atk=17+region_index*7 if is_boss else 9+region_index*5,
                boss=is_boss)


def combat_turn(p, enemy, action, turn, rng):
    """หนึ่งเทิร์น: ตรวจคำสั่งก่อนแก้ข้อมูล และไม่ให้ศัตรูที่ตายแล้วโจมตีกลับ"""
    if action not in ('1', '2', '3', '4'):
        raise ValueError('คำสั่งไม่ถูกต้อง')
    if p['hp'] <= 0 or enemy['hp'] <= 0:
        raise ValueError('การต่อสู้นี้จบแล้ว')
    if action == '2' and p['energy'] < 2:
        raise ValueError('พลังสกิลไม่พอ ต้องมีอย่างน้อย 2')
    if action == '4' and (p['potions'] == 0 or p['hp'] == p['max_hp']):
        raise ValueError('ยาหมดแล้ว' if p['potions'] == 0 else 'พลังชีวิตเต็มอยู่')
    result = dict(damage=0, received=0, healed=0, heavy=turn % 3 == 0,
                  guarded=action == '3', won=False)
    if action in ('1', '2'):
        multiplier = 2.2 if action == '2' else 1
        result['damage'] = round(p['atk'] * multiplier * rng.uniform(0.92, 1.08))
        enemy['hp'] = max(0, enemy['hp'] - result['damage'])
        p['energy'] = p['energy'] - 2 if action == '2' else min(3, p['energy'] + 1)
    elif action == '3':
        p['energy'] = min(3, p['energy'] + 1)
    else:
        p['potions'] -= 1
        result['healed'] = heal(p, 55)
    if enemy['hp'] == 0:
        result['won'] = True
        return result
    result['received'] = round(enemy['atk'] * (2.5 if result['heavy'] else 1)
                               * (0.25 if result['guarded'] else 1))
    p['hp'] = max(0, p['hp'] - result['received'])
    return result


def award_victory(p, enemy):
    reward = 55 if enemy['boss'] else 25
    p['gold'] += reward
    p['wins'] += 1
    p['energy'] = min(3, p['energy'] + 1)
    return reward


def battle(p, enemy, rng):
    p['energy'] = min(3, p['energy'] + 1)
    turn = 1
    type_text(f"\nพบ {enemy['name']}! {'[ BOSS ]' if enemy['boss'] else ''}")
    while p['hp'] > 0 and enemy['hp'] > 0:
        show_status(p)
        print(f"\n{enemy['name']} HP {enemy['hp']}/{enemy['max_hp']} | เทิร์น {turn}")
        print('⚠ เตรียมท่าไม้ตาย! แนะนำตั้งรับ' if turn % 3 == 0 else '◇ ศัตรูเตรียมโจมตีปกติ')
        print(f"1 โจมตี (+1 พลัง) | 2 {p['skill']} (ใช้ 2 พลัง)")
        print('3 ตั้งรับ (ลดดาเมจ 75%, +1 พลัง) | 4 ดื่มยา (+55 HP, เสียเทิร์น)')
        action = choose('เลือก 1–4 | 0 ออก: ', ['1', '2', '3', '4'])
        try:
            result = combat_turn(p, enemy, action, turn, rng)
        except ValueError as error:
            print(error)
            continue  # คำสั่งใช้ไม่ได้ไม่เสียเทิร์น
        if result['damage']:
            attack_animation(p['skill'] if action == '2' else p['name'], result['damage'], action == '2')
        elif result['guarded']:
            type_text('◈ คุณยกโล่ตั้งรับอย่างมั่นคง')
        else:
            type_text(f"✚ ดื่มยา ฟื้น {result['healed']} HP")
        if result['won']:
            reward = award_victory(p, enemy)
            type_text(f"ชนะ {enemy['name']}! ได้รับ {reward} เหรียญ")
            return True
        print(f"{'ท่าไม้ตาย!' if result['heavy'] else 'ศัตรูโจมตีกลับ!'} −{result['received']} HP")
        turn += 1
    return False


def explore(p, rng):
    print('\nทางแยก: 1 ลำธาร (+10 HP) | 2 ล่าสมบัติ (+18 เหรียญ, เสีย 5–11 HP)')
    action = choose('เลือกเส้นทาง | 0 ออก: ', ['1', '2'])
    loading('กำลังเดินทาง')
    if action == '1':
        print(f"พักริมลำธาร ฟื้น {heal(p, 10)} HP")
    else:
        damage = min(rng.randint(5, 11), p['hp'] - 1)
        p['hp'] -= damage
        p['gold'] += 18
        print(f'พบสมบัติ +18 เหรียญ แต่ติดกับดัก −{damage} HP')


def upgrade(p):
    cost = 35 + p['upgrades'] * 15
    if p['gold'] < cost:
        raise ValueError('เหรียญไม่พอ')
    p['gold'] -= cost
    p['atk'] += 5
    p['upgrades'] += 1
    return cost


def buy_potion(p):
    if p['potions'] >= 5:
        raise ValueError('ถือยาได้สูงสุด 5 ขวด')
    if p['gold'] < 20:
        raise ValueError('เหรียญไม่พอ')
    p['gold'] -= 20
    p['potions'] += 1


def camp(p):
    type_text('\nกองไฟของผู้เดินทางกำลังส่องแสง...')
    while True:
        show_status(p)
        print(f"1 ตีบวก ATK +5 ({35+p['upgrades']*15} เหรียญ)")
        print('2 ซื้อยา (20 เหรียญ) | 3 พักฟื้นและเดินทางต่อ | 0 ออก')
        action = choose('เลือก: ', ['1', '2', '3'])
        try:
            if action == '1':
                print(f'ตีบวกสำเร็จ! ใช้ {upgrade(p)} เหรียญ')
            elif action == '2':
                buy_potion(p)
                print('ได้รับยา 1 ขวด')
            else:
                recovered = heal(p, round(p['max_hp'] * 0.32))
                p['energy'] = 3
                print(f'พักฟื้น {recovered} HP และเติมพลังสกิลเต็ม')
                return
        except ValueError as error:
            print(error)


def show_ending(p, won):
    print('\n' + '=' * 44)
    loading('ม่านเถ้าถ่านกำลังสลาย' if won else 'เปลวไฟกำลังริบหรี่')
    if won:
        type_text('มังกรราชันเถ้าถ่านล้มลง แสงสว่างกลับคืนสู่โลก')
        type_text('ตอนจบ: ผู้พิทักษ์เปลวไฟ')
        type_text('คุณกลับมาพร้อมความหวัง' if p['hp'] >= p['max_hp']*.5 else 'แม้บอบช้ำ คุณก็ไม่ปล่อยให้เปลวไฟดับลง')
    else:
        type_text('คุณล้มลง แต่ประกายไฟเล็ก ๆ ยังคงลอยอยู่')
        type_text('ตอนจบ: ประกายไฟที่ยังไม่ดับ')
        type_text('การเดินทางครั้งใหม่ยังรอคุณอยู่')
    show_status(p)
    print(f"ปราบศัตรู {p['wins']}/9 | ตีบวก {p['upgrades']} ครั้ง")
    print('=' * 44)


def play():
    for key, job in CLASSES.items():
        print(f"{key} {job['name']} | HP {job['hp']} / ATK {job['atk']}")
    key = choose('เลือกอาชีพ | 0 ออก: ', CLASSES)
    name = input('ชื่อตัวละคร (Enter ใช้ชื่อเริ่มต้น / 0 ออก): ').strip()
    if name == '0':
        raise ExitGame()
    p = create_player(key, name or 'ผู้ถือเปลวไฟ')
    rng = random.Random()
    type_text(f"\nการเดินทางของ {p['name']} เริ่มต้นขึ้น...")
    for region_index, region in enumerate(REGIONS):
        loading(f"\nเข้าสู่ {region['name']}")
        for encounter in range(3):
            boss = encounter == 2
            if boss:
                type_text(f"⚠ ประตูบอสอยู่ตรงหน้า: {region['boss']}")
            explore(p, rng)
            enemy = create_enemy(region_index, boss)
            if not battle(p, enemy, rng):
                show_ending(p, False)
                return
            if not (region_index == 2 and boss):
                camp(p)
    show_ending(p, True)


def main():
    global ANIMATION
    if '--fast' in sys.argv:
        ANIMATION = False
    print('EMBERFALL — ผู้พิทักษ์เปลวไฟ')
    print('พิมพ์ 0 ในเมนูเพื่อออก | เกมนี้ไม่บันทึกเมื่อปิดโปรแกรม')
    try:
        while True:
            print('\n1 เริ่มเกม | 2 เปิด/ปิดแอนิเมชัน | 0 จบโปรแกรม')
            option = choose('เลือก: ', ['1', '2'])
            if option == '2':
                ANIMATION = not ANIMATION
                print('แอนิเมชัน: ' + ('เปิด' if ANIMATION else 'ปิด'))
            else:
                play()
                print('\nกลับสู่เมนูหลักแล้ว เลือก 1 เพื่อเล่นใหม่ หรือ 0 เพื่อจบเกม')
    except (ExitGame, KeyboardInterrupt, EOFError):
        print()
        type_text('เปลวไฟจะรอคุณอยู่เสมอ...')
        print('จบเกมแล้ว ขอบคุณที่เล่นครับ')


if __name__ == '__main__':
    main()
