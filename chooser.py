#!/usr/bin/env python3

from typing import Any
import os
import csv
import pprint
import math

from argparse import ArgumentParser


# Data fromhttps://twdnml.fandom.com/wiki/Survivor_Stats
# OCR'd by https://www.newocr.com/
hero_boosts = {
    "Aaron":            { "Damage": 0.10, "Health": 0.10 },
    "Abraham":          { "Damage": 0.10, "Health": 0.15 },
    "Alpha":            { "Damage": 0.10, "Health": 0.15 },
    "Beta":             { "Damage": 0.30, "Health": 0.40 },
    "Beth":             { "Damage": 0.25, "Health": 0.25 },
    "Carl":             { "Damage": 0.25, "Health": 0.15 },
    "Carol":            { "Damage": 0.25, "Health": 0.25 },
    "Connie":           { "Damage": 0.25, "Health": 0.25 },
    "Daryl":            { "Damage": 0.15, "Health": 0.20 },
    "Dwight":           { "Damage": 0.10, "Health": 0.10 },
    "Eugene":           { "Damage": 0.20, "Health": 0.20 },
    "Ezekiel":          { "Damage": 0.20, "Health": 0.15 },
    "Fighter Rosita":   { "Damage": 0.33, "Health": 0.33 },
    "Gabriel":          { "Damage": 0.20, "Health": 0.15 },
    "Glenn":            { "Damage": 0.10, "Health": 0.10 },
    "Governor":         { "Damage": 0.20, "Health": 0.05 },
    "Guardian Carol":   { "Damage": 0.10, "Health": 0.15 },
    "Hershell":         { "Damage": 0.20, "Health": 0.20 },
    "Hilltop Maggie":   { "Damage": 0.33, "Health": 0.33 },
    "Huntsman Daryl":   { "Damage": 0.33, "Health": 0.33 },
    "Jerry":            { "Damage": 0.10, "Health": 0.30 },
    "Jesus":            { "Damage": 0.30, "Health": 0.30 },
    "Maggie":           { "Damage": 0.10, "Health": 0.15 },
    "Mercer":           { "Damage": 0.20, "Health": 0.05 },
    "Merle":            { "Damage": 0.10, "Health": 0.10 },
    "Michonne":         { "Damage": 0.30, "Health": 0.15 },
    "Morgan":           { "Damage": 0.30, "Health": 0.15 },
    "Negan":            { "Damage": 0.30, "Health": 0.10 },
    "Princess":         { "Damage": 0.15, "Health": 0.10 },
    "Rick":             { "Damage": 0.20, "Health": 0.20 },
    "Riot Gear Glenn":  { "Damage": 0.33, "Health": 0.33 },
    "Rosita":           { "Damage": 0.15, "Health": 0.10 },
    "Rufus":            { "Damage": 0.00, "Health": -0.15 },
    "Sasha":            { "Damage": 0.15, "Health": 0.15 },
    "Shane":            { "Damage": 0.20, "Health": 0.20 },
    "Sniper Morgan":    { "Damage": 0.33, "Health": 0.33 },
    "Survivalist Rick": { "Damage": 0.33, "Health": 0.33 },
    "Tara":             { "Damage": 0.10, "Health": 0.10 },
    "Tyreese":          { "Damage": 0.30, "Health": 0.40 },
    "T-Dog":            { "Damage": 0.20, "Health": 0.20 },
    "Yumiko":           { "Damage": 0.10, "Health": 0.10 },
}

trait_boosts = {
    "Bullet Dodge": {
        "type": "Chance",
        "values": [ 0.0, .10, .14, .20, .24, .30, .32, .34, .36, .38, .40 ]
    },
    "Defensive Stance": {
        "type": "Damage Resistance",
        "values": [ 0.0, .30, .34, .38, .42, .45, .48, .51, .54, .57, .60 ]
    },
    "Dodge": {
        "type": "Chance",
        "values": [ 0.0, .05, .07, .10, .12, .15, .16, .17, .18, .19, .20 ]
    },
    "Iron skin": {
        "type": "Damage Resistance",
        "values": [ 0.0, .05, .07, .10, .12, .15, .16, .17, .18, .19, .20 ]
    },
    "Lucky": {
        "type": "Chance",
        "values": [ 0.0, .10, .12, .14, .16, .18, .20, .22, .23, .24, .25]
    },
    "Retaliate": {
        "type": "Pct Total Damage",
        "values": [ 0.0, .25, .37, .50, .62, .75, .78, .80, .83, .85, .87]
    },
    "Ruthless": {
        "type": "Charge Damage",
        "values": [ 0.0, .10, .13, .17, .21, .25, .29, .33, .37, .41, .45]
    },
    "Vigilant": {
        "type": "Overwatch Damage",
        "values": [ 0.0, .20, .24, .28, .32, .35, .38, .41, .44, .48, .50]
    },
    "Critcal Aim (normal)": {
        "type": "Chance",
        "values": [ 0.0, .03, .04, .05, .06, .07, .08, .09, .10, .11, .12]
    },
    "Critical Aim (critical)": {
        "type": "Chance",
        "values": [ 0.0, .18, .21, .24, .27, .30, .33, .36, .39, .42, .45]
    },
    "Marksman": {
        "type": "Damage",
        "values": [ 0.0, .05, .07, .10, .12, .15, .16, .17, .18, .19, .20]
    },
    "Revenge": {
        "type": "Overwatch Damage",
        "values": [ 0.0, .50, .53, .56, .60, .64, .68, .73, .78, .84, .90]
    },
    "Sure Shot": {
        "type": "Chance",
        "values": [ 0.0, .20, .25, .30, .35, .40, .43, .45, .48, .50, .53]
    },
    "Follow Through": {
        "type": "Chance",
        "values": [ 0.0, .25, .30, .35, .40, .43, .45, .48, .50, .55, .60]
    },
    "Power Strike": {
        "type": "Damage",
        "values": [ 0.0, .20, .25, .30, .35, .40, .43, .45, .48, .50, .53]
    },
    "Perseverance": {
        "type": "Chance",
        "values": [ 0.0, .18, .21, .24, .27, .30, .33, .36, .39, .42, .45 ]
    },
    "Strong": {
        "type": "Damage",
        "values": [ 0.0, .05, .07, .10, .12, .15, .16, .17, .18, .19, .20]
    },
    "Weakening": {
        "type": "Chance",
        "values": [ 0.0, .21, .24, .27, .30, .33, .36, .39, .42, .45, .50]
    },
    "Punish": {
        "type": "Pct Damage",
        "values": [ 0.0, .50, .55, .60, .65, .70, .80, .90, .100, .110, .120 ]
    }
}
base_details = {
    "Scout": {
        "Damage": [0, 49, 57, 65, 75, 86, 99, 114, 131, 150, 173, 198,
                   229, 263, 302, 347, 399, 459, 528, 607, 698, 830,
                   987, 1174, 1396, 1659, 1973, 2345, 2789, 3316,
                   3942, 4687, 5573, 6626, 7878, 9367, 11137, 13242,
                   15745, 18721, 22259, 26466, 31468, 37415, 44486,
                   52894, 62891, 74777, 88910, 105714, 125693],

        "Health": [0, 100, 111, 124, 140, 156, 174, 196, 219, 245,
                   289, 325, 365, 411, 462, 520, 586, 660, 741, 855,
                   984, 1156, 1384, 1634, 1943, 2310, 2747, 3266,
                   3883, 4616, 5489, 6526, 7159, 9226, 10970, 13043,
                   15508, 18439, 21923, 26067, 30993, 36851, 43816,
                   52097, 61943, 73650, 87570, 104120, 123799, 147197,
                   175017]
    },
    "Bruiser": {
        "Damage": [0, 33, 39, 44, 51, 58, 66, 76, 88, 102, 117, 134,
                   154, 178, 204, 234, 269, 310, 356, 409, 470, 559,
                   665, 791, 940, 1117, 1328, 1579, 1878, 2233, 2655,
                   3156, 3753, 4462, 5305, 6308, 7500, 8917, 10602,
                   12606, 14988, 17821, 21189, 25194, 29955, 35616,
                   42348, 50351, 59868, 71183, 84636],
        "Health": [0, 137, 154, 172, 193, 215, 241, 270, 302, 338,
                   397, 447, 503, 566, 637, 717, 808, 909, 1022, 1172,
                   1349, 1585, 1884, 2240, 2663, 3167, 3765, 4476,
                   5322, 6328, 7524, 8946, 10637, 12647, 15037, 17879,
                   21258, 25276, 30053, 35733, 42486, 50516, 60063,
                   71415, 84913, 100961, 120042, 142730, 169706,
                   201781, 239917]
    },
    "Warrior": {
        "Damage": [0, 45, 52, 60, 69, 79, 90, 105, 119, 137, 166, 192,
                   222, 256, 295, 341, 393, 455, 526, 608, 702, 835,
                   993, 1181, 1404, 1669, 1984, 2359, 2805, 3335,
                   3965, 4714, 5605, 6664, 7923, 9421, 11201, 13318,
                   15835, 18828, 22386, 26617, 31648, 37629, 44741,
                   53197, 63251, 75206, 89419, 106320, 126414],
        "Health": [0, 101, 114, 127, 142, 160, 179, 200, 223, 250,
                   289, 325, 365, 412, 463, 520, 586, 660, 741, 847,
                   975, 1145, 1362, 1619, 1925, 2289, 2721, 3236,
                   3847, 4574, 5438, 6466, 7688, 9141, 10869, 12923,
                   15365, 18269, 21722, 25828, 30709, 36513, 43414,
                   51619, 61374, 72974, 86766, 103165, 122663, 145846,
                   173411]
    },
    "Hunter": {
        "Damage": [0, 40, 46, 53, 61, 70, 80, 93, 106, 122, 141, 162,
                   186, 214, 246, 283, 325, 374, 430, 495, 569, 677,
                   805, 957, 1138, 1353, 1608, 1912, 2273, 2703, 3214,
                   3821, 4543, 5402, 6422, 7636, 9079, 10795, 12835,
                   15261, 18145, 21575, 25652, 30500, 36265, 43119,
                   51268, 60957, 72478, 86176, 102464],
        "Health": [0, 83, 92, 103, 116, 130, 145, 163, 182, 204, 229,
                   256, 287, 321, 360, 403, 452, 506, 566, 643, 741,
                   870, 1034, 1230, 1462, 1738, 2066, 2457, 2921,
                   3473, 4129, 4910, 5838, 6941, 8252, 9812, 11666,
                   13871, 16493, 19610, 23316, 27723, 32962, 39192,
                   46599, 55406, 65878, 78329, 93133, 110735, 131664]
    },
    "Shooter": {
        "Damage": [0, 43, 50, 57, 65, 76, 87, 99, 114, 132, 151, 173,
                   199, 229, 264, 303, 348, 400, 460, 530, 608, 723,
                   860, 1022, 1216, 1445, 1718, 2043, 2429, 2888,
                   3434, 4083, 4854, 9772, 6862, 8159, 9701, 11535,
                   13715, 16307, 19389, 23053, 27410, 32591, 38750,
                   46074, 54782, 65135, 77446, 92083, 109487],
        "Health": [0, 93, 105, 117, 130, 147, 164, 184, 205, 230, 258,
                   289, 323, 362, 405, 454, 508, 569, 637, 722, 831,
                   976, 1160, 1379, 1640, 1950, 2318, 2756, 3277,
                   3897, 4633, 5508, 6549, 7187, 9259, 11009, 13089,
                   15563, 18504, 22001, 26159, 31104, 36982, 43972,
                   52282, 62163, 73912, 87881, 104491, 124239, 147721]
    },
    "Assault": {
        "Damage": [0, 31, 37, 42, 48, 54, 62, 72, 83, 95, 110, 125,
                   145, 166, 191, 219, 252, 290, 333, 383, 440, 524,
                   623, 740, 880, 1046, 1244, 1479, 1758, 2090, 2485,
                   2955, 3513, 4177, 4966, 5905, 7021, 8348, 9925,
                   11801, 14032, 16683, 19836, 23585, 28043, 33343,
                   39645, 47138, 56046, 66639, 79234],
        "Health": [0, 101, 113, 126, 142, 158, 178, 198, 223, 249,
                   279, 313, 350, 392, 438, 491, 551, 616, 690, 785,
                   903, 1061, 1261, 1499, 1783, 2119, 2520, 2996,
                   3562, 4235, 5036, 5987, 7119, 8464, 10064, 11966,
                   14227, 16916, 20113, 23914, 28434, 33808, 40198,
                   47795, 56828, 67569, 80339, 95523, 113577, 135043,
                   160566]
    },
}

class_critical_boost = {
    'Assault': 0.25,
    'Bruiser': 0.25,
    'Scout': 0.50,
    'Hunter': 0.50,
    'Warrior': 0.50,
    'Shooter': 0.50
}

class Badge:
    set: str
    slot: int
    type: str
    raw_increase: int
    pct_increase: int
    stars: int
    raw_bonus: int
    pct_bonus: int
    bonus_type: str
    bonus_target: str
    pct_actual_bonus: int

    def __init__(self, row: dict[str, str]):
        self.set = row['Set']
        self.slot = int(row['Slot'])
        self.type = row['Type']
        self.raw_increase = int(row['Increase']) if row['Increase'] != '' else 0
        self.pct_increase = int(row['Increase %']) if row['Increase %'] != '' else 0
        self.stars = int(row['Stars']) if row['Stars'] != '' else 0
        self.raw_bonus = int(row['Bonus']) if row['Bonus'] != '' else 0
        self.pct_bonus = int(row['Bonus %']) if row['Bonus %'] != '' else 0
        self.bonus_type = row['Bonus Type']
        self.bonus_target = row['Bonus Target']

    def __str__(self):
        return '{{ {}-{}-{:<2} {:<5} Inc %: {:<2} Bon %: {:<2} Bon Type: {:<5} Bon Tgt: {:<10} Act Incr: {}}}'.format(
            self.set, self.slot, self.type, "*" * self.stars, self.pct_increase, self.pct_bonus, self.bonus_type, self.bonus_target, self.pct_actual_bonus)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if ( self.set == other.set and
             self.slot == other.slot and
             self.type == other.type and
             self.raw_increase == other.raw_increase and
             self.pct_increase == other.pct_increase and
             self.stars == other.stars and
             self.raw_bonus == other.raw_bonus and
             self.pct_bonus == other.pct_bonus and
             self.bonus_type == other.bonus_type and
             self.bonus_target == other.bonus_target ):
            return True

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

class BadgeSet:
    badges: list[Badge]
    set_counts: dict[str, int]
    type_counts: dict[str, int]
    type_increases: dict[str, float]
    reroll_set: bool = False

    def __init__(self,
                 badges: list[Badge],
                 reroll_set: bool = False,
                 reroll_slot: bool = False,
                 reroll_bonus: bool = False):
        self.init_structs()
        self.badges = badges

        self.reroll_set = reroll_set
        self.reroll_slot = reroll_slot
        self.reroll_bonus = reroll_bonus

        for badge in self.badges:
            self.set_counts[badge.set] += 1
            self.type_counts[badge.type] += 1
        self.compute_increases()

    def init_structs(self):
        self.set_counts = { 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0 }
        self.type_increases = { 'H': 0.0, 'D': 0.0, 'CC': 0.0, 'CD': 0.0, 'DR': 0.0 }
        self.type_counts = { 'H': 0, 'D': 0, 'CC': 0, 'CD': 0, 'DR': 0 }

    def reset_increases(self):
        for increase in self.type_increases:
            self.type_increases[increase] = 0.0

    def compute_increases(self):
        self.reset_increases()
        for badge in self.badges:
            incr: float = float(badge.pct_actual_bonus)

            if self.reroll_set or self.set_counts[badge.set] >= 4:
                incr *= 1.2

            self.type_increases[badge.type] += incr

    def has_set_bonus(self, set: str) -> bool:
        if self.reroll_set:
            return True

        if self.set_counts[set] >= 4:
            return True
        else:
            return False

    @property
    def improvement(self):
        self.compute_increases()
        return sum(self.type_increases.values())

    def __str__(self):
        output: str = f'Reroll Set = {self.reroll_set} | Reroll Slot = {self.reroll_slot} | Reroll Bonus = {self.reroll_bonus}\n'
        for badge in self.badges:
            output += ' {},\n'.format(badge)
        output += '\n'
        for type in self.type_increases:
            if self.type_increases[type] != 0.0:
                output += f' - {type} has total increase of {self.type_increases[type]:.1f}\n'
        output += '========================\n'
        output += f'{self.improvement:.1f} total improvement'
        return output

class Character:
    name: str
    teammates: list[str]
    badge_types: list[str]
    available_badges: list[Badge]
    computed_badges: list[Badge]
    type_focus: str

    def __init__(self,
                 name,
                 survivor_class,
                 character_details: dict[str, Any],
                 teammates: list[str] = [],
                 badge_types: list[str] = [],
                 badges: list[Badge] = [],
                 type_focus: str = ''):
        self.name = name
        self.survivor_class = survivor_class
        self.teammates = teammates
        self.badge_types = badge_types
        self.available_badges = badges.copy()
        self.type_focus = type_focus
        self.character_details = character_details
        self.chosen_set = []
        self.damage = 0

        self.reroll_slot = False
        self.reroll_set = False
        self.reroll_bonus = False

        self.compute_actual_bonus()

    def set_restrictions(self,
                         reroll_slot: bool = False,
                         reroll_set: bool = False,
                         reroll_bonus: bool = False):
        self.reroll_slot = reroll_slot
        self.reroll_set = reroll_set
        self.reroll_bonus = reroll_bonus

        self.compute_actual_bonus()


    def get_damage(self) -> float:
        # print(f'Survivor Level:  {self.character_details["Level"]}')
        class_base = base_details[self.survivor_class]['Damage'][self.character_details['Level']]
        if self.name in hero_boosts:
            hero_boost = hero_boosts[self.name]['Damage']
        else:
            hero_boost = 0.0

        trait_bsts = self.get_trait_boost('Damage')

        base_level = int(self.character_details['Stars'][0])

        if base_level <= 5:
            stars_modifier = base_level * 0.10 - 0.10
        else:
            stars_modifier = 0.4 + (base_level - 5) * 0.05

        base_damage = math.floor(class_base * ( 1.0 + hero_boost + stars_modifier))
        weapon_damage = 13717.0

        damage_badges = self.get_badge_boost('D')
        # print(f'Damage Badges:  {damage_badges}')
        # print(f'Damage Badges same set: {damage_badges * 1.2}')

        self.damage = math.floor( (base_damage + weapon_damage) * (1.0 + trait_bsts) * (1.0 + damage_badges) )

        return self.damage

    def get_trait_boost(self, type: str):
        traits = self.character_details['Traits'][::-1]
        # print(f'Stars - {self.character_details["Stars"]}')
        base_level = int(self.character_details['Stars'][0])
        ramped_levels = int(self.character_details['Stars'][1])

        trait_bsts = 0.0

        for trait in traits:
            if ramped_levels > 0:
                level_delta = 1
            else:
                level_delta = 0
            ramped_levels -= 1

            if trait in trait_boosts and trait_boosts[trait]['type'] == type:
                # print(f'Adding {trait_boosts[trait]["values"][base_level - level_delta - 1]} for {trait} @ {base_level - level_delta - 1}')
                trait_bsts += trait_boosts[trait]['values'][base_level - level_delta - 1]

        return trait_bsts

    def get_badge_boost(self, type: str):
        traits = self.character_details['Traits'][::-1]
        badge_boost = 0.0
        for badge in self.chosen_set.badges:
            if badge.type == type:
                # print(f' -- Adding base pct increase of {badge.pct_increase / 100.0}')
                badge_boost += ((badge.pct_increase / 100.0) * (1.2 if self.chosen_set.has_set_bonus(badge.set) else 1.0))
                if badge.bonus_type == 'Trait' and badge.bonus_target in traits:
                    # print(f' -- Adding bonus of {badge.pct_bonus / 100.0} due to {badge.bonus_target}')
                    badge_boost += ((badge.pct_bonus / 100.0) * (1.2 if self.chosen_set.has_set_bonus(badge.set) else 1.0))
                if badge.bonus_type == 'Role' and badge.bonus_target in self.teammates:
                    # print(f' -- Adding bonus of {badge.pct_bonus / 100.0} due to {badge.bonus_target}')
                    badge_boost += ((badge.pct_bonus / 100.0) * (1.2 if self.chosen_set.has_set_bonus(badge.set) else 1.0))
            # print(f' -- badge_boost now {badge_boost}')
        return badge_boost

    def get_critical_damage(self):
        class_crit_boost = class_critical_boost[self.survivor_class]

        trait_bsts = self.get_trait_boost('Critical Damage')

        critical_damage_badges = self.get_badge_boost('CD')

        self.critical_damage = math.floor(self.damage * (1 + class_crit_boost + trait_bsts + critical_damage_badges))
        # print(f'Crit Damage:  {self.damage} * (1 + {class_crit_boost} + {trait_bsts} + {damage_badges}) = {self.damage * (1 + class_crit_boost + trait_bsts + damage_badges)}')
        return self.critical_damage

    # def get_charge_damage(self):
    #     class_chrg_boost = class_charge_boost[self.survivor_class]

    #     trait_bsts = 0.0

    #     for trait in traits:
    #         if ramped_levels > 0:
    #             level_delta = 1
    #         else:
    #             level_delta = 0
    #         ramped_levels -= 1

    #         if trait in trait_boosts and trait_boosts[trait]['type'] == 'Critical Damage':
    #             print(f'Adding {trait_boosts[trait]["values"][base_level - level_delta - 1]} for {trait} @ {base_level - level_delta - 1}')
    #             trait_bsts += trait_boosts[trait]['values'][base_level - level_delta - 1]

    #     damage_badges = 0.0
    #     for badge in self.chosen_set.badges:
    #         if badge.type == 'D':
    #             print(f' -- Adding base pct increase of {badge.pct_increase / 100.0}')
    #             damage_badges += (badge.pct_increase / 100.0)
    #             if badge.bonus_type == 'Trait' and badge.bonus_target in traits:
    #                 print(f' -- Adding bonus of {badge.pct_bonus / 100.0} due to {badge.bonus_target}')
    #                 damage_badges += (badge.pct_bonus / 100.0)
    #             if badge.bonus_type == 'Role' and badge.bonus_target in self.teammates:
    #                 print(f' -- Adding bonus of {badge.pct_bonus / 100.0} due to {badge.bonus_target}')
    #                 damage_badges += (badge.pct_bonus / 100.0)
    #         print(f' -- damage_badges now {damage_badges}')

    #     print(f'Damage Badges:  {damage_badges}')
    #     print(f'Damage Badges same set: {damage_badges * 1.2}')
    #     damage_badges *= 1.2

    #     self.critical_damage = self.damage * (1 + class_crit_boost + trait_bsts + damage_badges)
    #     print(f'Crit Damage:  {self.damage} * (1 + {class_crit_boost} + {trait_bsts} + {damage_badges}) = {self.damage * (1 + class_crit_boost + trait_bsts + damage_badges)}')
    #     return self.critical_damage

    def compute_actual_bonus(self):
        """Compute the actual increase based on the character's traits and the
        roles of the teammates.  This computation is independent of whether
        the badge is selected.  A set bonus could still apply to the badge."""

        self.computed_badges = []

        if len(self.teammates) == 0 or len(self.available_badges) == 0:
            return

        # For each available badge, compute the actual bonus
        # percentage based on this survivor.  Copy the badge over to
        # self.computed_badges.
        for badge in self.available_badges:
            if self.reroll_bonus:
                badge.pct_actual_bonus = badge.pct_increase + badge.pct_bonus
            else:
                if badge.bonus_type == 'Trait':
                    if badge.bonus_target in self.character_details['Traits']:
                        if badge.pct_increase != '':
                            badge.pct_actual_bonus = badge.pct_bonus + badge.pct_increase
                        else:
                            badge.pct_actual_bonus = 0
                            # Don't take into account non % badges
                            # badge['Actual Bonus'] = badge['Bonus'] + badge['Increase']
                    else:
                        badge.pct_actual_bonus = badge.pct_increase
                elif badge.bonus_type == 'Role':
                    if badge.bonus_target in self.teammates:
                        if badge.pct_increase != '':
                            badge.pct_actual_bonus = badge.pct_bonus + badge.pct_increase
                        else:
                            badge.pct_actual_bonus = 0
                    else:
                        badge.pct_actual_bonus = badge.pct_increase
                else:
                    badge.pct_actual_bonus = badge.pct_increase

            self.computed_badges.append(badge)
        self.computed_badges = sorted(self.computed_badges,
                                      key=lambda b: b.pct_actual_bonus)

    def filter_badges_by_type(self,
                              badge_types: list[str],
                              badges: list[Badge]) -> list[Badge]:
        """Filter the provided list of badges by the badge_types specified
        for this survivor"""
        type_badges: list[Badge] = []
        for badge in badges:
            if badge.type in badge_types:
                type_badges.append(badge)
        return type_badges

    def filter_badges_by_set(self,
                             set: str,
                             badges: list[Badge]) -> list[Badge]:
        """Filter the provided list of badges by the specified set."""
        set_badges: list[Badge] = []
        for badge in badges:
            if badge.set == set:
                set_badges.append(badge)
        return set_badges

    def filter_badges_by_slot(self,
                              slot: int,
                              badges: list[Badge]) -> list[Badge]:
        """Filter the provided list of badges by the specified slot."""
        slot_badges: list[Badge] = []
        for badge in badges:
            if badge.slot == slot:
                slot_badges.append(badge)
        return slot_badges

    def filter_badges_by_traits(self,
                                traits: list[str],
                                badges: list[Badge]) -> list[Badge]:
        """Filter the provided list of badges by the specified set."""
        trait_badges: list[Badge] = []
        for badge in badges:
            if badge.bonus_target in traits:
                trait_badges.append(badge)
        return trait_badges

    # If self.reroll_slot is true, then there won't be a restriction to
    # choose a badge that fits a slot.  The expectation is that the
    # badge might need to be re-rolled for a better slot.
    def find_best_badges(self,
                         badges: list[Badge]) -> BadgeSet:
        slots_used: list[int] = []
        type_count: dict[str, int] = {}
        selected_badges: list[Badge] = []
        avail_badges: list[Badge] = self.computed_badges.copy()

        # Initialize the type counts
        for type in self.badge_types:
            type_count[type] = 0

        # Sort the provided list of badges by the actual bonus pct
        trait_badges = self.filter_badges_by_traits(self.character_details['Traits'], badges)
        # print('Badge selection')
        # pprint.pprint(trait_badges)
        best = sorted(trait_badges,
                      key=lambda d: d.pct_actual_bonus,
                      reverse=True)
        # print('Best selection')
        # pprint.pprint(best)

        # if self.name == 'Connie':
        #     pprint.pprint(best)
        #     # pprint.pprint(self.filter_badges_by_traits(self.character_details['Traits'], self.computed_badges))

        # get top three that don't overlap slot
        for badge in best:
            if self.reroll_slot or badge.slot not in slots_used:
                if badge.type in self.badge_types and type_count[badge.type] < 3:
                    type_count[badge.type] += 1
                    slots_used.append(badge.slot)
                    selected_badges.append(badge)
                    avail_badges.remove(badge)
                    badges.remove(badge)
            if len(selected_badges) == (len(self.badge_types) * 3):
                break

        # print('Selected so far:')
        # pprint.pprint(selected_badges)

        # print("Selected badges length = {}".format(str(len(selected_badges))))
        if len(selected_badges) != 6:
            # print(selected_badges)
            for slot in [1, 2, 3, 4, 5, 6]:
                if self.reroll_slot or slot not in slots_used:
                    needed: list[str] = []
                    for type in type_count:
                        if type_count[type] != 3 and type not in needed:
                            needed.append(type)
                    if len(needed) != 0:
                        # new_badge = self.find_badge(slot, needed, self.computed_badges)
                        new_badge = self.find_badge(slot, needed, badges)
                        # print('New badge:  ', end='')
                        # pprint.pprint(new_badge)
                        if new_badge is None:
                            new_badge = self.find_badge(slot, needed, avail_badges)

                        new_badge = self.find_better_badge(new_badge, avail_badges)
                        type_count[new_badge.type] += 1
                        slots_used.append(slot)
                        selected_badges.append(new_badge)
                        if new_badge in badges: badges.remove(new_badge)
                        if new_badge in avail_badges: avail_badges.remove(new_badge)

        selected_badges = sorted(selected_badges, key=lambda d: d.slot)
        # print('Selected badges:')
        # pprint.pprint(selected_badges)
        return BadgeSet(selected_badges, self.reroll_set, self.reroll_slot, self.reroll_bonus)

    def find_better_badge(self,
                          badge: Badge,
                          avail_badges: list[Badge]) -> Badge:
        """Given a specific badge, find out if there is a better badge
        in avail_badges that is a close match."""

        search_set = badge.set
        search_bonus = badge.bonus_target
        search_slot = badge.slot

        badges = self.filter_badges_by_type([ badge.type ],
                                            avail_badges)

        if not self.reroll_set:
            badges = self.filter_badges_by_set(badge.set, badges)
        if not self.reroll_bonus:
            badges = self.filter_badges_by_traits([ badge.bonus_target ], badges)
        if self.reroll_slot:
            badges = self.filter_badges_by_slot(badge.slot, badges)

        badges = sorted(badges,
                        key=lambda d: d.pct_actual_bonus,
                        reverse=True)

        # print('Filtered and sorted badges:')
        # pprint.pprint(badges)

        if len(badges) != 0 and badges[0].pct_actual_bonus > badge.pct_actual_bonus:
            return badges[0]
        else:
            return badge



    def find_badge(self,
                   slot: int,
                   types: list[str],
                   badges: list[Badge]) -> Badge:
        # print("Looking for a badge.  self.reroll_slot is {}".format(self.reroll_slot))
        # for tp in types:
        #     print("Needed type:  {}".format(tp))

        choices: list[Badge] = []
        for badge in badges:
            if (self.reroll_slot or badge.slot == slot) and badge.type in types:
                choices.append(badge)

        if len(choices) != 0:
            choices = sorted(choices, key=lambda d: d.pct_actual_bonus)
            # print("Choices has {} items.".format(len(choices)))
            return choices[0]
        else:
            return None

    def compute_possibilities(self) -> BadgeSet:
        """Compute BadgeSets six ways: First by just looking at the bonuses.
        Then looking at each of the sets in turn to find out whether those are
        any better with bonuses."""

        chosen_set: BadgeSet = None

        type_badges: list[Badge] = self.filter_badges_by_type(self.badge_types,
                                                              self.computed_badges)

        # First, compute the badges without set considered if self.reroll_set is True
        if self.reroll_set:
            # print('picking badges willy-nilly')
            chosen_set = self.find_best_badges(type_badges)
        # print('{} set: {}'.format(self.name, chosen_set))

        # Go through all the different sets and find a badge set that
        # is best out of them all
        for set in ['A', 'B', 'C', 'D', 'E']:
            # if self.name == 'Connie':
            #     print(f'===> Looking at set {set}')
            type_and_set_badges = self.filter_badges_by_set(set, type_badges)
            new_set = self.find_best_badges(type_and_set_badges)
            # if self.name == 'Connie':
            #     print('===>   find_best_badges')
            #     pprint.pprint(new_set.badges)
            if chosen_set is None:
                chosen_set = new_set
            if self.type_focus != '':
                # print('DEBUG:  character                 = {self.name}')
                # print('        chosen_set.improvement    = {chosen_set.improvement}')
                # print('        new_set.improvement       = {new_set.improvement}')
                # si_check = (chosen_set.improvement > (new_set.improvement + 5.0))
                # print('          check:                    {si_check}')
                # print('        chosen_set.type_increases = {chosen_set.type_increases[self.type_focus]}')
                # print('        new_set.type_increases    = {new_set.type_increases[self.type_focus]}')
                # ti_check = ((chosen_set.type_increases[self.type_focus] + 5.0) > new_set.type_increases[self.type_focus])
                # print('          check:                    {ti_check}')
                # If the chosen set is 5 points better, but the
                # chosen_set's type_focus is within a few points of
                # the new set's type_focus, then keep the chosen_set
                if (chosen_set.improvement > (new_set.improvement + 5.0)) and \
                   ((chosen_set.type_increases[self.type_focus] + 5.0) > new_set.type_increases[self.type_focus]):
                    chosen_set = chosen_set
                else:
                    if new_set.type_increases[self.type_focus] > chosen_set.type_increases[self.type_focus]:
                        chosen_set = new_set
            else:
                if new_set.improvement > chosen_set.improvement:
                    chosen_set = new_set

        self.chosen_set = chosen_set
        return chosen_set

def get_unused_badges(badges: list[Badge], stars: int) -> list[Badge]:
    unused: list[Badge] = []
    for badge in badges:
        if badge.stars == stars:
            unused.append(badge)
    return unused

def parse_args():
    argparser = ArgumentParser(description="Walking Dead No Man's Land badge calculator")
    argparser.add_argument('-rS', '--reroll_set', dest='reroll_set', action='store_true', default=False,
                           help='Assume that badge sets will be re-rolled and do not consider that in calculations')
    argparser.add_argument('-rs', '--reroll_slot', dest='reroll_slot', action='store_true', default=False,
                           help='Assume that badge slots will be re-rolled and do not consider that in calculations')
    argparser.add_argument('-rb', '--reroll_bonus', dest='reroll_bonus', action='store_true', default=False,
                           help='Assume that badge bonuses will be re-rolled and do not consider that in calculations')
    argparser.add_argument('-S', '--survivor_file', dest='survivor_file', type=str, default='survivors.csv',
                           help='CSV file containing up-to-date TWD NML survivor data.')
    argparser.add_argument('-B', '--badge_file', dest='badge_file', type=str, default='badges.csv',
                           help='CSV file containing up-to-date TWD NML badge data.')
    arguments = argparser.parse_args()

    return arguments

def import_survivors(survivor_file):
    survivors = {}
    with open(survivor_file) as charfile:
        reader = csv.DictReader(charfile)
        for row in reader:
            survivor = {}
            if row['Hero'] == 'X':
                survivor['Hero'] = True
            else:
                survivor['Hero'] = False

            traits: list[str] = []
            traits.append(row['Trait1'])
            #row.pop('Trait1')
            traits.append(row['Trait2'])
            #row.pop('Trait2')
            traits.append(row['Trait3'])
            #row.pop('Trait3')
            traits.append(row['Trait4'])
            #row.pop('Trait4')
            traits.append(row['Trait5'])
            #row.pop('Trait5')
            survivor['Level'] = int(row['Lvl'])
            survivor['Stars'] = row['Stars'].split('.')
            survivor['Traits'] = traits
            survivor['Name'] = row['Person']
            #row.pop('Person')
            survivors[survivor['Name']] = survivor

    return survivors

def import_badges(badge_file):
    badges = []
    with open(badge_file) as badgefile:
        reader = csv.DictReader(badgefile)
        for row in reader:
            new_badge = Badge(row)
            badges.append(new_badge)
    return badges

def main():
    arguments = parse_args()
    if not os.path.isfile(arguments.badge_file):
        print(f' - Provided badge file ({arguments.badge_file}) is not valid')
        return
    if not os.path.isfile(arguments.survivor_file):
        print(f' - Provided survivor file ({arguments.survivor_file}) is not valid')
        return

    available_badges: list[Badge] = []
    survivors: dict[str, Any] = {}

    available_badges = import_badges(arguments.badge_file)
    survivors = import_survivors(arguments.survivor_file)

    results: dict[str, BadgeSet] = {}

    chars = {
        'Connie': { 'teammates': ['Assault', 'Shooter'],
                    'types': ['D', 'CD'],
                    'type_focus': 'CD',
                    'starting_bonus': { 'CC': 45 },
                    'class': 'Scout' },
        # 'Yumiko': { 'teammates': ['Assault', 'Scout'],
        #             'types': ['D', 'CD'],
        #             'type_focus': 'CD',
        #             'starting_bonus': { 'CC': 48 },
        #             'class': 'Shooter' },
        # 'Mercer': { 'teammates': ['Shooter', 'Scout'],
        #             'types': ['D', 'CD'],
        #             'type_focus': 'CD',
        #             'starting_bonus': { 'CC': 50 },
        #             'class': 'Assault' },
        # 'Sasha': { 'teammates': ['Shooter', 'Assault'],
        #            'types': ['CD', 'D'],
        #            'type_focus': 'D',
        #            'starting_bonus': { 'CC': 50 },
        #            'class': 'Hunter' },
        # 'Aaron': { 'teammates': ['Hunter', 'Shooter'],
        #            'types': ['D', 'CD'],
        #            'type_focus': 'CD',
        #            'starting_bonus': { 'CC': 45 },
        #            'class': 'Shooter' },
        # 'Eugene': { 'teammates': ['Bruiser', 'Bruiser'],
        #             'types': ['H', 'DR'],
        #             'type_focus': 'DR',
        #             'starting_bonus': { 'CC': 45 },
        #             'class': 'Bruiser'},
        # 'Morgan': { 'teammates': ['Bruiser', 'Bruiser'],
        #             'types': ['H', 'DR'],
        #             'type_focus': 'DR',
        #             'starting_bonus': { 'CC': 45 },
        #             'class': 'Bruiser'},
        # 'Negan': { 'teammates': ['Bruiser', 'Bruiser'],
        #             'types': ['H', 'DR'],
        #             'type_focus': 'DR',
        #             'starting_bonus': { 'CC': 45 }},
        # 'Michonne': { 'teammates': ['Hunter', 'Bruiser'],
        #               'types': ['D', 'DR'],
        #             'type_focus': 'D'  },
        # 'Abraham': { 'teammates': ['Hunter', 'Hunter'],
        #             'types': ['D', 'H'],
        #             'type_focus': 'H'  },
        # 'Daryl': { 'teammates': ['Shooter', 'Hunter'],
        #            'types': ['DR', 'D'],
        #            'type_focus': 'DR'  },
        # 'CarolH': { 'teammates': ['Shooter', 'Hunter'],
        #            'types': ['CC', 'CD'],
        #            'type_focus': 'CC'  },
        # 'Carl': { 'teammates': ['Hunter', 'Hunter'],
        #            'types': ['DR', 'H'],
        #            'type_focus': 'H'  },
        # 'Norman': { 'teammates': ['Hunter', 'Bruiser'],
        #             'types': ['D', 'CD'],
        #             'type_focus': 'D'  },
        # 'Maggie': { 'teammates': ['Shooter', 'Hunter'],
        #             'types': ['CD', 'CC'],
        #             'type_focus': 'CD'  },
    }

    built_chars = {}

    for name in chars:
        survivor = chars[name]
        # print('Total badges available:  {}'.format(len(badges)))
        char: Character = Character(name,
                                    survivor['class'],
                                    survivors[name],
                                    teammates=survivor['teammates'],
                                    badge_types=survivor['types'],
                                    badges=available_badges,
                                    type_focus=survivor['type_focus'])

        char.set_restrictions(reroll_slot=arguments.reroll_slot,
                                         reroll_set=arguments.reroll_set,
                                         reroll_bonus=arguments.reroll_bonus)
        res = char.compute_possibilities()

        # pprint.pprint(res.badges)

        for badge in res.badges:
            available_badges.remove(badge)
        results[char.name] = res
        # if survivor == 'Eugene':
        #     print(res)
        built_chars[char.name] = char

    for res in built_chars:
        print(f'{res}')
        print('========================================================================')
        print(f'{built_chars[res].chosen_set}')
        print(f'Damage:           {built_chars[res].get_damage()}')
        print(f'Critical Damage:  {built_chars[res].get_critical_damage()}')


    # print('Unused 5 Star Badges')
    # print('====================')
    # for unused in get_unused_badges(available_badges, stars=5):
    #     print(unused)


if __name__ == '__main__':
    main()
