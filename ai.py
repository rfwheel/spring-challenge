import sys
import math

TYPE_MONSTER = 0
TYPE_HERO = 1

THREAT_NEUTRAL = 0
THREAT_MINE = 1

base_x, base_y = [int(i) for i in input().split()]
heroes_per_player = int(input())  # Always 3
center_x = 17630.0 / 2
center_y = 9000.0 / 2
slope = (center_y - base_y) / (center_x - base_x)
theta = math.atan(slope)
SIDE = 0 if base_x == 0 else 1
control_toggle = 0
control_points = [
    [(17630, 4300), (12930, 9000)],
    [(0,4700), (4700,0)],
]
home_dist = 7000
home_points = [
    [
        (int(home_dist*math.cos(math.pi/4)), int(home_dist*math.sin(math.pi/4))),
        (int(home_dist*math.cos(math.pi/12)), int(home_dist*math.sin(math.pi/12))),
        (int(home_dist*math.cos(5*math.pi/12)), int(home_dist*math.sin(5*math.pi/12))),
    ],
]
home_points.append(
    [
        (17630 - home_points[0][0][0], 9000 - home_points[0][0][1]),
        (17630 - home_points[0][1][0], 9000 - home_points[0][1][1]),
        (17630 - home_points[0][2][0], 9000 - home_points[0][2][1]),
    ],
)
mana = 0

class Monster:
    def __init__(self, tag, x, y, health, vx, vy, shield_life):
        self.tag = int(tag)
        self.x = int(x)
        self.y = int(y)
        self.health = int(health)
        self.vx = int(vx)
        self.vy = int(vy)
        self.base_dist = math.sqrt((base_x - x)**2 + (base_y - y)**2)
        self.shield = shield_life
        self.redirected = False

    def calc_hero_dists(self, hero_list):
        self.hero_dists = [math.sqrt((h.x - self.next_xpos())**2 + (h.y - self.next_ypos())**2) for h in hero_list]

    def next_xpos(self):
        return self.x + self.vx

    def next_ypos(self):
        return self.y + self.vy

    def get_next_dist(self, x, y):
        return math.sqrt((x - self.next_xpos())**2 + (y - self.next_ypos())**2)


class Hero:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.i = index
        self.action = None

    def set_target(self, target):
        global control_toggle

        if self.should_cast_control(target):
            target.redirected = True
            control_toggle = control_toggle ^ 1
            control_x = control_points[SIDE][control_toggle][0]
            control_y = control_points[SIDE][control_toggle][1]
            self.action = f"SPELL CONTROL {target.tag} {control_x} {control_y}"
            return

        if self.should_attack(target):
            x = target.next_xpos()
            y = target.next_ypos()
            self.action = f"MOVE {x} {y}"
            return

    def get_action(self, defense_list, neutral_list):
        if self.action:
            return self.action

        defense_list.sort(key=lambda x: 50000*x.base_dist + x.hero_dists[self.i])
        for threat in defense_list:
            self.set_target(threat)
            if self.action is not None:
                return self.action

        neutral = self.get_farming_target(neutral_list)
        if neutral is not None:
            return f"MOVE {neutral.next_xpos()} {neutral.next_ypos()}"

        homex = home_points[SIDE][self.i][0]
        homey = home_points[SIDE][self.i][1]
        return f"MOVE {homex} {homey}"

    def get_dist(self, x, y):
        return math.sqrt((x - self.x)**2 + (y - self.y)**2)

    def should_attack(self, monster):
        if monster.redirected:
            return False

        if monster.base_dist < 5500:
            return True

        if self.get_dist(monster.next_xpos(), monster.next_ypos()) > 2500:
            return False

        return True

    def should_cast_control(self, monster):
        if mana < 10:
            return False
        if self.get_dist(monster.x, monster.y) > 2200:
            return False
        if monster.health < 15:
            return False
        if monster.base_dist < 4500:
            return False
        if monster.shield > 0:
            return False
        if monster.redirected:
            return False
        return True

    def get_farming_target(self, neutral_list):
        homex = home_points[SIDE][self.i][0]
        homey = home_points[SIDE][self.i][1]
        for neutral in neutral_list:
            if self.get_dist(neutral.next_xpos(), neutral.next_ypos()) > 3000:
                continue
            if neutral.get_next_dist(homex, homey) > 3000:
                continue
            return neutral


def sort_defense_list(defense_list):
    defense_list.sort(key=lambda x: x.base_dist)
    return defense_list

def take_actions(hero_list, defense_list, neutral_list):
    if len(defense_list) == 0:
        for hero in hero_list:
            print(hero.get_action(defense_list, neutral_list))
        return

    if len(defense_list) == 1:
        for hero in hero_list:
            hero.set_target(defense_list[0])
            print(hero.get_action(defense_list, neutral_list))
        return

    secondary_targeted = False
    for i in range(len(hero_list)):
        if ((defense_list[0].hero_dists[i] == max(defense_list[0].hero_dists)) and (not secondary_targeted)):
            hero_list[i].set_target(defense_list[1])
            secondary_targeted = True
        else:
            hero_list[i].set_target(defense_list[0])

    for hero in hero_list:
        print(hero.get_action(defense_list, neutral_list))

# game loop
while True:
    for i in range(2):
        # health: Each player's base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        health, mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see

    hero_list = []
    defense_list = []
    neutral_list = []

    for i in range(entity_count):
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]
        if _type == TYPE_HERO:
            hero_list.append(Hero(x, y, len(hero_list)))
        if threat_for == THREAT_MINE:
            defense_list.append(Monster(_id, x, y, health, vx, vy, shield_life))
        if threat_for == THREAT_NEUTRAL:
            neutral_list.append(Monster(_id, x, y, health, vx, vy, shield_life))
    
    ##### GAME LOGIC

    defense_list = sort_defense_list(defense_list)
    for m in defense_list:
        m.calc_hero_dists(hero_list)

    take_actions(hero_list, defense_list, neutral_list)


