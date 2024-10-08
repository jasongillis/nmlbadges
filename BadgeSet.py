from Badge import Badge

class BadgeSet:
    set_counts: dict[str, int]
    type_counts: dict[str, int]
    reroll_set: bool = False
    reroll_slot: bool = False
    reroll_bonus: bool = False

    def __init__(self,
                 badges: list[Badge],
                 bonus_targets: list[str],
                 reroll_set: bool = False,
                 reroll_slot: bool = False,
                 reroll_bonus: bool = False):

        self.slots: dict[int, list[Badge]] = {
            1: [], 2: [], 3: [], 4: [], 5: [], 6: []
        }

        self.reroll_set = reroll_set
        self.reroll_slot = reroll_slot
        self.reroll_bonus = reroll_bonus

        self.bonus_targets = bonus_targets

        for badge in badges:
            self.add_badge(badge)

        self.mark_badges()


    def mark_badges(self):
        """Mark items in each badge in the set that need to be rerolled
        for maximum effect."""
        for slot in range(1,7):
            for badge in self.slots[slot]:
                badge.mark(self.most_set(),
                           slot,
                           len(self.slots[slot]),
                           self.bonus_targets,
                           reroll_set=self.reroll_set,
                           reroll_slot=self.reroll_slot,
                           reroll_bonus=self.reroll_bonus)

    def badge_count(self) -> int:
        """Return the number of badges in the set"""
        count = 0

        for slot in range(1,7):
            count += len(self.slots[slot])

        return count

    def badges(self) -> list[Badge]:
        """Return the badges in the set as a list"""
        badges: list[Badge] = []

        for slot in range(1,7):
            for badge in self.slots[slot]:
                badges.append(badge)

        return badges

    def bonus_set(self) -> str:
        """Return the set that has bonus enabled"""
        set_counts = { 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0 }
        for slot in range(1,7):
            for badge in self.slots[slot]:
                set_counts[badge.set] += 1

        for set_name in ['A', 'B', 'C', 'D', 'E']:
            if set_counts[set_name] >= 4:
                return set_name

        return ''

    def most_set(self) -> str:
        """Return the set that has bonus enabled"""
        set_counts = { 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0 }
        for slot in range(1,7):
            for badge in self.slots[slot]:
                set_counts[badge.set] += 1

        biggest_set = ''
        biggest_set_count = 0
        for set_name in ['A', 'B', 'C', 'D', 'E']:
            if set_counts[set_name] > biggest_set_count:
                biggest_set = set_name
                biggest_set_count = set_counts[set_name]
            # if set_counts[set_name] >= 4:
            #     return set

        return biggest_set

    def reroll_count(self) -> str:
        """Determine the number of rerolls required for this set to
        achieve maximum effect"""
        reroll_count = 0
        most_set = self.most_set()
        slot_counts = { i: 0 for i in range(1,7) }
        for slot in range(1, 7):
            for badge in self.slots[slot]:
                slot_counts[badge.slot] += 1
                if most_set != badge.set:
                    reroll_count += 1
                if badge.bonus_target not in self.bonus_targets:
                    reroll_count += 1

        # pprint(slot_counts)
        for slot in slot_counts:
            if slot_counts[slot] == 0: reroll_count += 1

        return reroll_count

    def types(self) -> list[str]:
        """Return a list of badge types in this badge set"""
        types: set[str] = set([])

        for slot in range(1,7):
            for badge in self.slots[slot]:
                types.add(badge.type)

        return list(types)

    def type_count(self, type: str) -> int:
        """Return the number of badges for the specified type"""
        count: int = 0

        for slot in range(1,7):
            for badge in self.slots[slot]:
                if badge.type == type: count += 1

        return count

    def add_badge(self, badge: Badge) -> bool:
        """Try to add a badge to the set.  Returns false if the badge
        cannot be added."""

        # If slot re-rolling isn't allowed and there's already a badge
        # in the slot, then can't add.
        # Set rerolling and bonus rerolling don't affect badge addition
        if not self.reroll_slot and len(self.slots[badge.slot]) != 0:
            return False

        # Only 3 badges of each type are allowed
        if self.type_count(badge.type) < 3:
            self.slots[badge.slot].append(badge)
            return True

        return False

    def type_increase(self, type: str) -> float:
        """Compute and return the total increase for the specified
        badge type"""
        increase_pct: float = 0.0
        bonus_set: str = self.bonus_set()

        for slot in range(1,7):
            for badge in self.slots[slot]:
                if badge.type == type:
                    badge_increase: float = badge.pct_increase
                    if (badge.bonus_target in self.bonus_targets or
                        self.reroll_bonus):
                        badge_increase += badge.pct_bonus
                    if badge.set == bonus_set:
                        badge_increase *= 1.2
                    increase_pct += badge_increase

        return increase_pct

    def improvement(self) -> float:
        """Determine the total improvement for this set over the base
        survivor details"""
        improvement = 0.0
        for type in ['D', 'CD', 'CC', 'H', 'DR']:
            improvement += self.type_increase(type)
        return improvement

    def print_stat_block(self,
                         damage: int,
                         crit_damage: int,
                         charge_damage: int):
        output = f'{self}'
        output += '-------------------------------------------------------------------------------------------\n'

        improvement: float = 0.0

        damage_strs = [
            f'               |  {damage: >7d} - New damage',
            f'               |  {crit_damage: >7d} - New critical damage',
            f'               |  {charge_damage: >7d} - New charge damage'
        ]

        for i, type in enumerate(sorted(self.types(), reverse=True)):
            type_incr = self.type_increase(type)
            output += f'   {type_incr: 4.1f} increase for {type: <2}      {damage_strs[i]}\n'
            improvement += type_incr
        output += f'  ---------------             {damage_strs[2]}\n'
        output += f'   {improvement:>4.1f} total improvement (with {self.reroll_count(): >2} rerolls) |'
        return output

    def __str__(self):
        output = ( f'          ' +
                   f'Reroll Set = {self.reroll_set} | ' +
                   f'Reroll Slot = {self.reroll_slot} | ' +
                   f'Reroll Bonus = {self.reroll_bonus}\n' )
        for badge in self.badges():
            output += ' {}\n'.format(badge)
        return output
