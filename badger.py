#!/usr/bin/env python3

import os
import csv

from argparse import ArgumentParser

from Badge import Badge
from BadgeSet import BadgeSet
from Survivor import Survivor

chars = {
    'Yumiko': { 'teammates': ['Assault', 'Scout'],
                'types': ['D', 'CD'],
                'class': 'Shooter' },
    'Mercer': { 'teammates': ['Shooter', 'Scout'],
                'types': ['D', 'CD'],
                'class': 'Assault' },
    'Connie': { 'teammates': ['Assault', 'Shooter', 'Yumiko', 'Mercer' ],
                'types': ['D', 'CD'],
                'class': 'Scout' },
    'Sasha': { 'teammates': ['Shooter', 'Assault'],
               'types': ['D', 'CD'],
               'class': 'Hunter' },
    'Ezekiel': { 'teammates': ['Assault', 'Scout', 'Mercer', 'Connie'],
                 'types': ['D', 'CD'],
                 'class': 'Warrior' },
    'Tyreese': { 'teammates': ['Warrior', 'Scout', 'Ezekiel', 'Connie'],
                 'types': ['D', 'CD'],
                 'class': 'Warrior' },
    'Aaron': { 'teammates': ['Hunter', 'Shooter'],
               'types': ['D', 'CD'],
               'class': 'Shooter' },
    'Fighter Rosita': { 'teammates': ['Bruiser', 'Morgan', 'Protector Daryl'],
                        'types': ['H', 'DR'],
                        'class': 'Bruiser'},
    'Morgan': { 'teammates': ['Bruiser', 'Bruiser', 'Fighter Rosita', 'Protector Daryl'],
                'types': ['H', 'DR'],
                'class': 'Bruiser'},
    'Protector Daryl': { 'teammates': ['Bruiser', 'Morgan', 'Fighter Rosita'],
                         'types': ['H', 'DR'],
                         'class': 'Bruiser' },
    'Daryl': { 'teammates': ['Shooter', 'Hunter'],
               'types': ['DR', 'D'],
               'class': 'Hunter' },
    'CarolH': { 'teammates': ['Shooter', 'Hunter'],
                'types': ['CC', 'CD'],
                'class': 'Hunter' },
    'Carl': { 'teammates': ['Hunter', 'Hunter'],
              'types': ['DR', 'H'],
              'class': 'Shooter' },
    'Norman': { 'teammates': ['Hunter', 'Bruiser'],
                'types': ['D', 'CD'],
                'class': 'Hunter' },
    'Maggie': { 'teammates': ['Shooter', 'Hunter'],
                'types': ['CD', 'CC'],
                'class': 'Shooter' },
}

def get_unused_badges(badges: list[Badge], min_stars: int) -> list[Badge]:
    unused: list[Badge] = []
    for badge in badges:
        if badge.stars >= min_stars:
            unused.append(badge)
    return unused

def consume_badges(badge_set: BadgeSet, badge_list: list[Badge]) -> list[Badge]:
    if badge_set is None:
        return badge_list

    for badge in badge_set.badges():
        if badge in badge_list:
            badge_list.remove(badge)
        else:
            print(f'badge is not in badge_list:\n{badge}')

    return badge_list

def save_unused_badges(badges: list[Badge], filename: str):
    with open(filename, 'w') as csvfile:
        fields = [ 'Set', 'Slot', 'Type', 'Increase',
                   'Increase %', 'Stars', 'Bonus',
                   'Bonus %', 'Bonus Type', 'Bonus Target' ]

        writer = csv.DictWriter(csvfile, fieldnames=fields)

        writer.writeheader()

        for badge in badges:
            writer.writerow(badge.get_dict())

def parse_args():
    argparser = ArgumentParser(prog='badger.py', description="Walking Dead No Man's Land badge calculator")
    argparser.add_argument('-rS', '--reroll_set', dest='reroll_set', action='store_true', default=False,
                           help='Assume that badge sets will be re-rolled and do not consider that in calculations')
    argparser.add_argument('-rs', '--reroll_slot', dest='reroll_slot', action='store_true', default=False,
                           help='Assume that badge slots will be re-rolled and do not consider that in calculations')
    argparser.add_argument('-rb', '--reroll_bonus', dest='reroll_bonus', action='store_true', default=False,
                           help='Assume that badge bonuses will be re-rolled and do not consider that in calculations')
    argparser.add_argument('-m', '--max_rerolls', dest='max_rerolls', type=int, default=5,
                           help='The maximum number of rerolls allowed per survivor badge set')
    argparser.add_argument('-s', '--min_stars', dest='min_stars', type=int, default=4,
                           help='Minimum number of stars a badge must have to be considered')
    argparser.add_argument('-S', '--survivor_file', dest='survivor_file', type=str,
                           default='survivors.csv', metavar='FILENAME',
                           help='CSV file containing up-to-date TWD NML survivor data.')
    argparser.add_argument('-B', '--badge_file', dest='badge_file', type=str,
                           default='badges.csv', metavar='FILENAME',
                           help='CSV file containing up-to-date TWD NML badge data.')
    argparser.add_argument('-u', '--unused_badges', dest='save_badges', type=str,
                           default='', metavar='FILENAME',
                           help='After selecting badges, save the unused badges to the specified file')
    arguments = argparser.parse_args()

    return arguments

def import_survivors(survivor_file: str):
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
            traits.append(row['Trait2'])
            traits.append(row['Trait3'])
            traits.append(row['Trait4'])
            traits.append(row['Trait5'])

            survivor['Weapon Damage'] = int(row['Weapon'])
            survivor['Level'] = int(row['Lvl'])
            survivor['Stars'] = row['Stars'].split('.')
            survivor['Traits'] = traits
            survivor['Name'] = row['Person']
            survivors[survivor['Name']] = survivor

    return survivors

def import_badges(badge_file: str, min_stars: int = 4):
    badges = []
    with open(badge_file) as badgefile:
        reader = csv.DictReader(badgefile)
        for row in reader:
            new_badge = Badge(row)
            if new_badge.stars >= min_stars:
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

    available_badges = import_badges(arguments.badge_file,
                                     min_stars = arguments.min_stars)
    survivors = import_survivors(arguments.survivor_file)

    built_chars = {}

    for name in chars:
        survivor = chars[name]

        char: Survivor = Survivor(name,
                                  survivor['class'],
                                  survivors[name],
                                  teammates=survivor['teammates'],
                                  badge_types=survivor['types'],
                                  max_rerolls=arguments.max_rerolls)

        char.set_restrictions(reroll_slot=arguments.reroll_slot,
                              reroll_set=arguments.reroll_set,
                              reroll_bonus=arguments.reroll_bonus)

        char.find_best_badge_set(available_badges)
        available_badges = consume_badges(char.badge_set, available_badges)
        print(f'{char.name}:  Building for {", ".join(sorted(survivor["types"], reverse=True))}')
        print('===========================================================================================')
        if char.badge_set is not None:
            print(char.badge_set.print_stat_block(char.get_damage(), char.get_critical_damage(), char.get_charge_damage()))
        else:
            print(' No badge set was generated with the provided restrictions!')
        print('===========================================================================================')
        print()
        print()

    if arguments.save_badges != '':
        save_unused_badges(available_badges, arguments.save_badges)

if __name__ == '__main__':
    main()
