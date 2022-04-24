import sys
import math

TYPE_MONSTER = 0
TYPE_HERO = 1

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
mana = 0

class Monster:
    def __init__(self, tag, x, y, health, vx, vy):
        self.tag = int(tag)
        self.x = int(x)
        self.y = int(y)
        self.health = int(health)
        self.vx = int(vx)
        self.vy = int(vy)
        self.dist = math.sqrt((base_x - x)**2 + (base_y - y)**2)
        self.redirected = False

    def calc_hero_dists(self, hero_list):
        self.hero_dists = [math.sqrt((h.x - self.next_xpos())**2 + (h.y - self.next_ypos())**2) for h in hero_list]

    def next_xpos(self):
        return self.x + self.vx

    def next_ypos(self):
        return self.y + self.vy


class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y
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

        x = target.next_xpos()
        y = target.next_ypos()
        self.action = f"MOVE {x} {y}"

    def get_action(self):
        if self.action:
            return self.action
        else:
            return "WAIT"

    def get_dist(self, x, y):
        return math.sqrt((x - self.x)**2 + (y - self.y)**2)

    def should_cast_control(self, monster):
        if mana < 10:
            return False
        if self.get_dist(monster.x, monster.y) > 2200:
            return False
        if monster.health < 17:
            return False
        if monster.redirected:
            return False
        return True


def sort_defense_list(defense_list):
    defense_list.sort(key=lambda x: x.dist)
    return defense_list

def take_actions(hero_list, defense_list):
    if len(defense_list) == 0:
        for hero in hero_list:
            print("WAIT")
        return

    if len(defense_list) == 1:
        for hero in hero_list:
            hero.set_target(defense_list[0])
            print(hero.get_action())
        return

    secondary_targeted = False
    for i in range(len(hero_list)):
        if ((defense_list[0].hero_dists[i] == max(defense_list[0].hero_dists)) and (not secondary_targeted)):
            hero_list[i].set_target(defense_list[1])
            secondary_targeted = True
        else:
            hero_list[i].set_target(defense_list[0])

    for hero in hero_list:
        print(hero.get_action())

# game loop
while True:
    for i in range(2):
        # health: Each player's base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        health, mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see

    hero_list = []
    defense_list = []

    for i in range(entity_count):
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]
        if _type == TYPE_HERO:
            hero_list.append(Hero(x, y))
        if threat_for == 1:
            defense_list.append(Monster(_id, x, y, health, vx, vy))
    
    ##### GAME LOGIC

    defense_list = sort_defense_list(defense_list)
    for m in defense_list:
        m.calc_hero_dists(hero_list)

    take_actions(hero_list, defense_list)


