
import math
import time

from typing import Any

from itertools import combinations

from pprint import pprint

from Badge import Badge
from BadgeSet import BadgeSet

class Survivor:
    name: str
    teammates: list[str]
    badge_types: list[str]
    available_badges: list[Badge]
    badge_set: BadgeSet

    def __init__(self,
                 name,
                 survivor_class,
                 character_details: dict[str, Any],
                 teammates: list[str] = [],
                 badge_types: list[str] = [],
                 # badges: list[Badge] = [],
                 max_rerolls: int = 4):
        self.name = name
        self.survivor_class = survivor_class
        self.teammates = teammates
        self.badge_types = badge_types
        # self.available_badges = badges.copy()
        self.character_details = character_details
        self.traits = character_details['Traits']
        self.bonus_targets = self.traits + self.teammates
        self.chosen_set = []
        self.damage = 0
        self.badge_set = None
        self.weapon_damage = character_details['Weapon Damage']
        self.reroll_slot = False
        self.reroll_set = False
        self.reroll_bonus = False

        self.max_rerolls = max_rerolls

    def set_restrictions(self,
                         reroll_slot: bool = False,
                         reroll_set: bool = False,
                         reroll_bonus: bool = False):
        self.reroll_slot = reroll_slot
        self.reroll_set = reroll_set
        self.reroll_bonus = reroll_bonus

    def get_damage(self, weapon_boost: float = 1.0) -> int:
        # print(f'Survivor Level:  {self.character_details["Level"]}')
        class_base = base_details[self.survivor_class]['Damage'][self.character_details['Level']]
        # print(f'Class base = {class_base}')

        base_level = int(self.character_details['Stars'][0])
        if base_level <= 5:
            stars_modifier = base_level * 0.10 - 0.10
        else:
            stars_modifier = 0.4 + (base_level - 5) * 0.05
        #print(f'Stars mod = {stars_modifier}')

        if self.name in hero_boosts:
            hero_boost = hero_boosts[self.name]['Damage']
        else:
            hero_boost = 0.0
        #print(f'Hero boost = {hero_boost}')

        #print(f'final base damage = {class_base * (1 + hero_boost + stars_modifier)}')

        trait_bsts = self.get_trait_boost('Damage')
        #print(f'Damage trait boost:  {trait_bsts}')

        # base_damage = math.floor(class_base * ( 1.0 + hero_boost + stars_modifier))
        base_damage = class_base * ( 1.0 + hero_boost + stars_modifier)
        weapon_damage = self.weapon_damage * weapon_boost

        #print(f'Damage without badges should be: {(base_damage + weapon_damage) * (1 + trait_bsts)}')

        damage_badges = self.get_badge_boost('D')
        # print(f'Damage Badges:  {damage_badges}')
        # print(f'Damage Badges same set: {damage_badges * 1.2}')

        self.damage = math.floor( (base_damage + weapon_damage) *
                                  (1.0 + trait_bsts) *
                                  (1.0 + damage_badges) )

        return int(self.damage)

    def get_trait_boost(self, type: str) -> float:
        """Get the boost for the provided damage type due to traits."""
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
                trait_bsts += trait_boosts[trait]['values'][base_level - level_delta - 1]

        return trait_bsts

    def get_badge_boost(self, type: str) -> float:
        traits = self.bonus_targets
        badge_boost = 0.0
        for badge in self.badge_set.badges():
            if badge.type == type:
                bonus_set_mult = 1.0
                if self.badge_set.bonus_set() == badge.set:
                    bonus_set_mult = 1.2

                increase = badge.pct_increase
                if badge.bonus_target in self.bonus_targets:
                    increase += badge.pct_bonus

                badge_boost += ((increase / 100.0) * bonus_set_mult)
        return badge_boost

    def get_critical_damage(self, weapon_boost: float = 1.0) -> int:
        class_crit_boost = class_critical_boost[self.survivor_class]

        trait_bsts = self.get_trait_boost('Critical Damage')

        critical_damage_badges = self.get_badge_boost('CD')

        if self.damage == 0:
            self.damage = self.get_damage(weapon_boost)

        crit_damage = (1 + class_crit_boost +
                       trait_bsts + critical_damage_badges)
        self.critical_damage = math.floor(self.damage * crit_damage)

        return int(self.critical_damage)

    def get_charge_damage(self) -> int:
        class_chrg_boost = class_charge_weapon_boost[self.survivor_class]

        charge_weapon_boost = class_charge_weapon_boost[self.survivor_class]
        charge_damage = self.get_critical_damage(charge_weapon_boost)

        if self.survivor_class in ['Shooter', 'Scout']:
            charge_damage *= 1.5

        trait_bsts = self.get_trait_boost('Charge Damage')
        charge_damage *= (1.0 + trait_bsts)

        self.charge_damage = math.floor(charge_damage)

        return int(self.charge_damage)


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
                             set_names: list[str],
                             badges: list[Badge]) -> list[Badge]:
        """Filter the provided list of badges by the specified set."""
        set_badges: list[Badge] = []
        for badge in badges:
            if badge.set in set_names:
                set_badges.append(badge)
        return set_badges

    def filter_badges_by_slot(self,
                              slots: list[int],
                              badges: list[Badge]) -> list[Badge]:
        """Filter the provided list of badges by the specified slot."""
        slot_badges: list[Badge] = []
        for badge in badges:
            if badge.slot in slots:
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

    def compute_actual_bonus(self, available_badges: list[Badge]):
        """Compute the actual increase based on the character's traits and the
        roles of the teammates.  This computation is independent of whether
        the badge is selected.  A set bonus could still apply to the badge."""
        if len(available_badges) == 0:
            return
        # For each available badge, compute the actual bonus
        # percentage based on this survivor.

        for badge in available_badges:
            if self.reroll_bonus:
                badge.pct_actual_bonus = badge.pct_increase + badge.pct_bonus
            else:
                if badge.bonus_target in self.bonus_targets:
                    if badge.pct_increase != '':
                        badge.pct_actual_bonus = badge.pct_bonus + badge.pct_increase
                    else:
                        badge.pct_actual_bonus = (badge.raw_increase + badge.raw_bonus) / 1000.0
                        # Don't take into account non % badges
                        # badge['Actual Bonus'] = badge['Bonus'] + badge['Increase']
                else:
                    if badge.pct_increase != '':
                        badge.pct_actual_bonus = badge.pct_increase
                    else:
                        badge.pct_actual_bonus = (badge.raw_increase) / 1000.0

    # NEW METHOD
    # A. For each set, do the following:
    #   1. Generate set of badges based on a set (at least 4)
    #   2. For the open 1 or 2 slots or the two slots that have the
    #      lowest pct_actual_bonus, look at badges from other sets
    #      (following reroll options) to replace or fill spots.
    # B. Compare the damage and critical damage outputs on each set
    #    to see which is better.
    def find_best_badge_set(self,
                            available_badges: list[Badge]) -> BadgeSet:
        chosen_set: BadgeSet = None
        best_improvement = 0.0
        best_set = None
        best_set_name = ''
        similar_sets = 0

        all_sets = ['A', 'B', 'C', 'D', 'E']
        # all_sets = [ 'C', 'E' ]
        rep_set = []
        rep_value = 0

        # Update the badges with the correct bonus increases for this
        # survivor
        self.compute_actual_bonus(available_badges)

        for set_name in all_sets:
            new_value, new_set = self.build_badge_set(set_name,
                                                      available_badges)
            if new_set is None:
                # print('new_set is None')
                continue

            # If a set of badges was found that was less than 6
            # badges, fill in the missing slots with other badges
            if len(new_set) != 6:
                # print(f'{set_name}:  new_set has {len(new_set)} badges')
                types_needed = { i: 3 for i in self.badge_types }
                slots_needed = { i: 1 for i in range(1,7) }
                for badge in new_set:
                    types_needed[badge.type] -= 1
                    slots_needed[badge.slot] -= 1

                type_list = [k for k, v in types_needed.items() if v > 0]
                slot_list = [k for k, v in slots_needed.items() if v == 1]
                set_names = [k for k in all_sets if k != set_name]

                rep_value, rep_set = self.find_replacement_badges(types_needed,
                                                                  slot_list,
                                                                  set_names,
                                                                  available_badges)

                new_set = new_set + rep_set
                new_value = new_value + rep_value

            new_bs = BadgeSet(new_set,
                              self.bonus_targets,
                              reroll_set=self.reroll_set,
                              reroll_slot=self.reroll_slot,
                              reroll_bonus=self.reroll_bonus)
            new_bs_improvement = new_bs.improvement()

            # Try replacing the "worst" two badges in the set to see
            # if a better outcome is found.
            sorted_set = sorted(new_set, key=lambda b: b.pct_actual_bonus)
            types_needed = { i: 0 for i in self.badge_types }
            slots_needed = set()
            types_needed[sorted_set[0].type] += 1
            slots_needed.add(sorted_set[0].slot)
            types_needed[sorted_set[1].type] += 1
            slots_needed.add(sorted_set[1].slot)
            set_names = [k for k in all_sets if k != set_name]
            adj_value = new_value - sorted_set[0].pct_actual_bonus - sorted_set[1].pct_actual_bonus
            avail_badges = available_badges.copy()
            for i in range(2,len(sorted_set) if len(sorted_set)<6 else 6):
                avail_badges.remove(sorted_set[i])
            # start_time = time.time()
            rep_value, rep_set = self.find_replacement_badges(types_needed,
                                                              list(slots_needed),
                                                              set_names,
                                                              avail_badges)
            adj_set = new_set.copy()
            adj_set.remove(sorted_set[0])
            adj_set.remove(sorted_set[1])
            adj_set += rep_set
            adj_bs = BadgeSet(adj_set,
                              self.bonus_targets,
                              reroll_set=self.reroll_set,
                              reroll_slot=self.reroll_slot,
                              reroll_bonus=self.reroll_bonus)
            adj_bs_improvement = adj_bs.improvement()

            if new_bs_improvement < adj_bs_improvement:
                new_bs = adj_bs
                new_bs_improvement = adj_bs_improvement

            new_set_rerolls = new_bs.reroll_count()
            if ( (new_set_rerolls <= self.max_rerolls) or
                 (best_set is None) ):
                if new_bs_improvement > best_improvement:
                    best_improvement = new_bs_improvement
                    best_set = new_bs
                    best_set_name = set_name
                    similar_sets = 0
                elif new_bs_improvement == best_improvement:
                    # If there's fewer rerolls required for the new set,
                    # pick it.
                    if best_set.reroll_count() > new_set_rerolls:
                        best_improvement = new_bs_improvement
                        best_set = new_bs
                        best_set_name = set_name
                    similar_sets += 1

        self.badge_set = best_set

        if similar_sets != 0:
            print(f'Found {similar_sets} other similar sets')

        return self.badge_set

    def find_replacement_badges(self,
                                types_needed: dict[str, int],
                                slots_needed: list[int],
                                set_names: list[str],
                                available_badges: list[Badge]) -> (int, list[Badge]):
        badges = self.filter_badges_by_slot(slots_needed, available_badges)

        badge_lists = { k: { 'badges': [], 'needed': v } for k, v in types_needed.items() if v != 0 }
        for type in badge_lists:
            badge_lists[type]['badges'] = self.filter_badges_by_type([type], badges)
        type_list = [k for k, v in types_needed.items() if v > 0]

        best_value = 0
        best_set = []

        first_max = badge_lists[type_list[0]]['needed'] + 1
        for first_counter in range(1, first_max):
            first_combinations = combinations(badge_lists[type_list[0]]['badges'],
                                              first_counter)

            for combo_first in first_combinations:
                first_value = 0
                first_occupancy = set()
                first_valid = True

                for badge in combo_first:
                    if badge.slot in first_occupancy:
                        first_valid = False
                        break
                    first_occupancy.add(badge.slot)
                    first_value += badge.pct_actual_bonus

                if len(type_list) == 2 and first_valid:
                    second_value = 0
                    second_valid = True
                    second_combo = []

                    second_max = badge_lists[type_list[1]]['needed'] + 1
                    for second_counter in range(1, second_max):
                        second_combinations = combinations(badge_lists[type_list[1]]['badges'],
                                                           second_counter)
                        for combo_second in second_combinations:
                            second_value = 0
                            second_occupancy = first_occupancy.copy()
                            second_valid = True
                            second_combo = []

                            for badge in combo_second:
                                if badge.slot in second_occupancy:
                                    second_valid = False
                                    break
                                second_occupancy.add(badge.slot)
                                second_value += badge.pct_actual_bonus

                            if second_valid:
                                second_combo = combo_second

                    if ( first_valid and second_valid and
                         (first_value + second_value) > best_value ):
                        best_value = first_value + second_value
                        best_set = list(combo_first) + list(second_combo)
                else:
                    if first_valid and first_value > best_value:
                        best_value = first_value
                        best_set = list(combo_first)


        return (best_value, best_set)

    def build_badge_set(self,
                        set_name: str,
                        badges: list[Badge]) -> (int, list[Badge]):
        type_badges = badges.copy()
        type_badges = self.filter_badges_by_type(self.badge_types,
                                                 type_badges)
        type_badges = sorted(type_badges, key=lambda b: (b.pct_actual_bonus, b.set, b.slot), reverse=True)

        filtered_badges = type_badges

        if not self.reroll_set:
            filtered_badges = self.filter_badges_by_set([ set_name ], type_badges)

        if not self.reroll_bonus:
            filtered_badges = self.filter_badges_by_traits(self.bonus_targets,
                                                           filtered_badges)

        # Try all combinations of badges from each desired badge type.
        # This simply considers the pct_actual_bonus as the "value" of
        # each badge and uses that to compare sets.
        type1 = self.badge_types[0]
        type1_badges = self.filter_badges_by_type([ type1 ], filtered_badges)
        type2 = self.badge_types[1]
        type2_badges = self.filter_badges_by_type([ type2 ], filtered_badges)

        slots_type1 = { i: [] for i in range(1,7) }
        slots_type2 = { i: [] for i in range(1,7) }

        best_value = 0
        best_set = None
        best_set_rerolls = 0

        if len(type2_badges) < len(type1_badges):
            temp = type1_badges
            temp_type = type1
            type1_badges = type2_badges
            type1 = type2
            type2_badges = temp
            type2 = temp_type

        max_type1_combinations = len(list(combinations(type1_badges, 3))) + len(list(combinations(type1_badges, 2)))
        max_type2_combinations = len(list(combinations(type2_badges, 3))) + len(list(combinations(type2_badges, 2)))

        type1_iterations = 0
        type2_iterations = 0
        total_iterations = 0
        for count_type1 in range(2, 4):
            type1_combinations = combinations(type1_badges, count_type1)

            type2_iterations = 0

            for combo_type1 in type1_combinations:
                type1_value = 0
                type1_occupancy = set()
                type1_valid = True

                for badge in combo_type1:
                    if badge.slot in type1_occupancy and not self.reroll_slot:
                        type1_valid = False
                        break
                    type1_occupancy.add(badge.slot)
                    type1_value += badge.pct_actual_bonus

                if type1_valid:
                    type2_value = 0
                    type2_valid = True
                    type2_combo = []

                    new_value, new_set, new_set_rerolls = self.sub_combinations(
                        set_name, range(2,4), type2, type2_badges, type1_occupancy,
                        combo_type1, type_badges, type1_value, type1_valid)
                    type2_iterations += 1
                    total_iterations += 1

                    if ( (new_set_rerolls <= self.max_rerolls) or
                         (best_set is None) ):
                        if new_value > best_value:
                            best_value = new_value
                            best_set = new_set
                            best_set_rerolls = new_set_rerolls
                        elif new_value == best_value:
                            if new_set_rerolls < best_set_rerolls:
                                best_value = new_value
                                best_set = new_set
                                best_set_rerolls = new_set_rerolls

            type1_iterations += 1

        return (best_value, best_set)

    def store_set(badge_set_details):
        print(' - In storing')
        self.badges_to_process_lock.acquire()
        self.badges_to_process.append(badges)
        print(f'Len badges to process = {len(self.badges_to_process)}')
        self.badges_to_process_lock.release()
        print(' - Exiting storing')

    def sub_combinations(self,
                         set_name: str,
                         the_range,
                         badge_type: str,
                         badges: list[Badge],
                         other_occupancy: set[int],
                         other_combo: tuple[Badge, ...],
                         type_badges: list[Badge],
                         other_value: int,
                         other_valid: bool) -> (int, list[Badge], int):
        """Process combinations of badge_type items from badges
        to build out a full badge set."""
        # start_time = time.time()
        best_value = 0
        best_set = None
        best_set_rerolls = self.max_rerolls

        # Incoming type_badges has all badges for both types, filter
        # that to the specific one.
        this_type_badges = type_badges
        if badge_type is not None:
            this_type_badges = self.filter_badges_by_type([ badge_type ], type_badges)
        for count in the_range:
            sub_combos = combinations(badges, count)
            sub_combos = combinations(badges, count)

            for combo in sub_combos:
                value = 0
                occupancy = other_occupancy.copy()
                is_valid = True
                saved_combo = []

                for badge in combo:
                    slot_exists = badge.slot in occupancy
                    if slot_exists and not self.reroll_slot:
                        is_valid = False
                        break
                    occupancy.add(badge.slot)
                    value += badge.pct_actual_bonus

                if is_valid:
                    saved_combo = combo
                    if len(saved_combo) != 3:
                        saved_combo = self.fill_combo(badge_type,
                                                      set_name,
                                                      combo,
                                                      this_type_badges,
                                                      occupancy,
                                                      other_combo)

                if other_valid and is_valid:
                    new_value = other_value + value
                    new_set = list(other_combo) + list(saved_combo)
                    new_set_rerolls = self.count_rerolls(new_set, set_name)

                    if ( (new_set_rerolls <= self.max_rerolls) or
                         (best_set is None) ):
                        if new_value > best_value:
                            best_value = new_value
                            best_set = new_set
                            best_set_rerolls = new_set_rerolls
                        elif new_value == best_value:
                            if new_set_rerolls < best_set_rerolls:
                                best_value = new_value
                                best_set = new_set
                                best_set_rerolls = new_set_rerolls

        # end_time = time.time()
        # print(f' - {end_time - start_time}')
        return best_value, best_set, best_set_rerolls

    def fill_combo(self, type: str,
                   set_name: str,
                   combo: tuple[Badge, ...],
                   badges: list[Badge],
                   occupancy: set[int],
                   other_combo: set[Badge]):
        """When a badge combo is less than three badges, then find the best
        alternative badge to fill out that combo to three badges."""
        # If all the rerolls are enabled, then there isn't anything
        # else to be done.
        if self.reroll_set and self.reroll_bonus and self.reroll_slot:
            return combo

        avail_badges: list[Badge] = badges.copy()

        for badge in combo:
            avail_badges.remove(badge)

        # for badge in combo:
        #     print(f'{badge.short_str()} ', end='')
        # print()

        # sorted_badges = sorted(available_badges, key=lambda b: (b.pct_actual_bonus, b.set), reverse=True)
        if not self.reroll_slot:
            needed_slots = list(set([1,2,3,4,5,6]) - occupancy)
            avail_badges = self.filter_badges_by_slot(needed_slots, avail_badges)

        if not self.reroll_set:
            avail_badges = self.filter_badges_by_set([ set_name ], avail_badges)

        if len(avail_badges) > 0:
            return combo + (avail_badges[0],)
        else:
            return combo

    def count_rerolls(self, badges: list[Badge], set_name: str) -> int:
        """Count the number of rerolls required for this set."""
        count = 0
        slots = { i: -1 for i in range(1,7) }
        for badge in badges:
            slots[badge.slot] += 1
            if self.reroll_set and badge.set != set_name:
                count += 1
            if (self.reroll_bonus and
                badge.bonus_target not in self.bonus_targets):
                count += 1
        for slot in slots:
            count += slots[slot]

        return count


# Data from https://twdnml.fandom.com/wiki/Survivor_Stats
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
    "Outlaw Negan":     { "Damage": 0.33, "Health": 0.33 },
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
                   3434, 4083, 4854, 5772, 6862, 8159, 9701, 11535,
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

class_charge_weapon_boost = {
    'Assault': 1.0,
    'Bruiser': 1.4,
    'Scout': 1.2,
    'Hunter': 1.0,
    'Warrior': 1.0,
    'Shooter': 1.2,
}
