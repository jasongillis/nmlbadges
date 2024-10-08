class Badge:
    set: str = ''
    slot: int = 0
    type: str = ''
    raw_increase: int = 0
    pct_increase: int = 0
    stars: int = 0
    raw_bonus: int = 0
    pct_bonus: int = 0
    bonus_type: str = ''
    bonus_target: str = ''
    pct_actual_bonus: int = 0

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

        self.unmark()

    def get_dict(self):
        return {
            'Set': self.set,
            'Slot': self.slot,
            'Type': self.type,
            'Increase': self.raw_increase,
            'Increase %': self.pct_increase,
            'Stars': self.stars,
            'Bonus': self.raw_bonus,
            'Bonus %': self.pct_bonus,
            'Bonus Type': self.bonus_type,
            'Bonus Target': self.bonus_target
        }

    def mark(self,
             bonus_set: str,
             slot: str,
             slot_count: int,
             bonus_targets: list[str],
             reroll_set: bool = True,
             reroll_slot: bool = True,
             reroll_bonus: bool = True):
        """Mark the items in the badge that need to be rerolled"""
        if self.set != bonus_set:
            if reroll_set:
                self.reroll_set_mark = '^'
            else:
                self.reroll_set_mark = '+'
        else:
            self.reroll_set_mark = ' '

        if self.slot != slot or slot_count > 1:
            if reroll_slot:
                self.reroll_slot_mark = '^'
            else:
                self.reroll_slot_mark = '+'
        else:
            self.reroll_slot_mark = ' '

        if self.bonus_target not in bonus_targets:
            if reroll_bonus:
                self.reroll_bonus_mark = '^'
            else:
                self.reroll_bonus_mark = '+'
        else:
            self.reroll_bonus_mark = ' '

    def unmark(self):
        """Remove marks from the badge set"""
        self.reroll_set_mark = ' '
        self.reroll_slot_mark = ' '
        self.reroll_bonus_mark = ' '


    def __str__(self):
        return ' {}{} -{}{} - {:<2} {:<5} Inc %: {:<2} Bon %: {:<2} Bon Type: {:<5} Bon Tgt: {}{:<10.10} Act Incr: {}'.format(
            self.reroll_set_mark, self.set,
            self.reroll_slot_mark, self.slot,
            self.type, "*" * self.stars, self.pct_increase,
            self.pct_bonus, self.bonus_type,
            self.reroll_bonus_mark, self.bonus_target,
            self.pct_actual_bonus)

    def short_str(self):
        return ' {}{}{}{}-{:<2}-{}{}{}'.format(
            self.stars, self.set, self.slot, self.type, self.pct_increase, self.pct_bonus, self.bonus_target, self.pct_actual_bonus)

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
