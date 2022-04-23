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

class Monster:
    def __init__(self, x, y, health, vx, vy):
        self.x = int(x)
        self.y = int(y)
        self.health = int(health)
        self.vx = int(vx)
        self.vy = int(vy)
        self.dist = math.sqrt((base_x - x)**2 + (base_y - y)**2)


class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def calc_monster_dists(self, monsters):
        pairs = list(map(lambda m: (m, m.x, m.y), monsters))
        self.monsters = [(m, math.sqrt((mx - self.x)**2 + (my - self.y)**2)) for (m,mx,my) in pairs]
        self.monsters.sort(key=lambda m: m[1])

    def action(self):
        if len(self.monsters) == 0:
            return "WAIT"

        target = self.monsters[0][0]
        x = target.x + target.vx
        y = target.y + target.vy
        
        return f"MOVE {x} {y}"


def sort_monster_list(monster_list):
    monster_list.sort(key=lambda x: x.dist)
    return monster_list


# game loop
while True:
    for i in range(2):
        # health: Each player's base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        health, mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see

    hero_list = []
    monster_list = []

    for i in range(entity_count):
        # _id: Unique identifier
        # _type: 0=monster, 1=your hero, 2=opponent hero
        # x: Position of this entity
        # shield_life: Ignore for this league; Count down until shield spell fades
        # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
        # health: Remaining health of this monster
        # vx: Trajectory of this monster
        # near_base: 0=monster with no target yet, 1=monster targeting a base
        # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]
    
        if _type == TYPE_HERO:
            hero_list.append(Hero(x, y))

        if threat_for == 1:
            monster_list.append(Monster(x, y, health, vx, vy))
    
    monster_list = sort_monster_list(monster_list)
    for hero in hero_list:
        hero.calc_monster_dists(monster_list)

    for hero in hero_list:
        print(hero.action())

