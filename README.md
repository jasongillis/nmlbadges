# An automated chooser for TWD NML badges

```
usage: chooser.py [-h] [-rS] [-rs] [-rb] [-S SURVIVOR_FILE] [-B BADGE_FILE]
                  [-m MAX_REROLLS] [-s MIN_STARS]

Walking Dead No Man's Land badge calculator

options:
  -h, --help            show this help message and exit
  -rS, --reroll_set     Assume that badge sets will be re-rolled and do not
                        consider that in calculations
  -rs, --reroll_slot    Assume that badge slots will be re-rolled and do not
                        consider that in calculations
  -rb, --reroll_bonus   Assume that badge bonuses will be re-rolled and do not
                        consider that in calculations
  -S SURVIVOR_FILE, --survivor_file SURVIVOR_FILE
                        CSV file containing up-to-date TWD NML survivor data.
  -B BADGE_FILE, --badge_file BADGE_FILE
                        CSV file containing up-to-date TWD NML badge data.
  -m MAX_REROLLS, --max_rerolls MAX_REROLLS
                        The maximum number of rerolls allowed per survivor
                        badge set
  -s MIN_STARS, --min_stars MIN_STARS
                        Minimum number of stars a badge must have to be
                        considered
```

When running the program, note that adding all of `-rs`, `-rb`, and `-rS` will cause the search to take a VERY long time.  Limit the min
stars if you're doing this.  It's usually sufficient to specify just `-rb` or `-rS` with `-rs`.  Specifying all three is going to give combinations with a lot of badge rerolls required, which might not be helpful.

It's also helpful to run the program with several different selections of options to see what builds a better badge set for you.  You might not like the set generated without rerolls enabled, so enabling `-rb` or `-rs` might give you a set you're more comfortable with.

Specifying all three reroll options (`-rb`, `-rs`, and `-rS`) is going to take a very long time to run with large badge sets.

If you don't want to have a lot of rerolls, specify the max rerolls option, `-m`, to limit the number of rerolls per badge set.  This might prevent the tool from finding a valid set, for some survivors, though.

## Output

The program outputs a list of the badges for each survivor specified. The output looks like this:

```
Carl:  Building for H, DR
===========================================================================================
          Reroll Set = False | Reroll Slot = False | Reroll Bonus = True
  +A - 1 - DR ***** Inc %: 21 Bon %: 0  Bon Type: None  Bon Tgt: ^None       Act Incr: 21
   C - 2 - H  ****  Inc %: 15 Bon %: 4  Bon Type: Role  Bon Tgt: ^Warrior    Act Incr: 19
  +B - 3 - H  ****  Inc %: 15 Bon %: 4  Bon Type: Hero  Bon Tgt: ^Gabriel    Act Incr: 19
   C - 4 - DR ***** Inc %: 20 Bon %: 5  Bon Type: Hero  Bon Tgt: ^Ezekiel    Act Incr: 25
  +C - 5 - H  ****  Inc %: 15 Bon %: 4  Bon Type: Hero  Bon Tgt: ^Sasha      Act Incr: 19
   C - 6 - DR ****  Inc %: 15 Bon %: 4  Bon Type: Hero  Bon Tgt: ^Gabriel    Act Incr: 19
-------------------------------------------------------------------------------------------
    64.6 increase for H                      |    25765 - New damage
    73.8 increase for DR                     |    38647 - New critical damage
  ---------------                            |    57970 - New charge damage
   138.4 total improvement (with  8 rerolls) |
===========================================================================================
```

A total improvement value is provided that indicates how much better than no badges this badge set is for the survivor.  This value is the sum of the percentage improvements for each type badge that was searched.  It doesn't really make sense, but it's a way to compare sets.

Note that a badge item with a `+` or `^` next to it indicates where a re-roll is needed to achieve the calculated numbers.  A `+` indicates that an item should be re-rolled to be optimal, but it wasn't requested by a flag to the program.  A `^` indicates that a reroll is needed and that item was allowed to be rerolled by program flags.

The damage numbers are estimates as the calculation formulas available on the public wiki seem to break when accounging for badge bonuses.

## Specifying survivors

The `survivor.csv` file includes details of your survivors, but that is just data.  Youl will need to specify what survivors to build badge sets for and what types of badges that you want for each survivor. Currently, the tool only supports two badge types for each survivor, so you can do Damage and Critical Damage or Health and Damage Reduction, but not Damage, Health, and Critical Damage.

There is a dictionary at the top of the file called `chars` that specifies what survivors to build sets for.  This is the format for the dictionary:

```
chars = {
    '<SURVIVOR NAME>': {
        'teammates': [ '<CLASS OR NAME>', '<CLASS OR NAME>', '<CLASS OR NAME>', ... ],
        'types': [ 'D', 'CD' ],
        'class': 'Shooter'
    }
}
```

The values in types can be `D`, `CD`, `CC`, `H`, or `DR`.

The classes can be `Shooter`, `Bruiser`, `Assault`, `Scout`, or `Hunter`.

`teammates` should specify the classes and names of target teammates.  Generally, you're probably going to be building a badge set for a certain configuration of team, so you need to specify those folks here.  Ideally, you want to find badges that match the traits that your survivors have and not depend on specific heroes or classes for the bonus targets.  If you don't want to target specific heros, leave out the formal names and just specify classes.  This could lead to a lot of badge re-rolling.


## Badge Information
Badge information must be provided in a CSV file with the following columns:

| CSV Column | Data Description |
| --- | --- |
| Set	| The badge set.  One of 'A', 'B', 'C', 'D', 'E' |
| Slot | The badge slot.  Numeric 1-6. |
| Type | The badge type.  One of 'D' (Damage), 'CD' (Critical Damage), 'CC' (Critical Chance), 'H' (Health), or 'DR' (Damage Reduction) |
| Increase % | The percentage increase for the badge.  Expressed as an integer (e.g. 20) |
| Bonus %	| The percentage bonus increase if the bonus is matched.  Expressed as an integer (e.g. 5) |
| Bonus Target | The trait, role or hero that the bonus targets.  Names must match those in the survivor CSV. |
| Stars	| The number of stars the badge has.  Number 1-5. |
| Bonus Type | The bonus type.  One of 'Role', 'Trait', or 'Hero'. |
| Increase | For really old badges, the raw increase if it wasn't a percentage. |
| Bonus | For really old badges, the raw increase if it wasn't a percentage. |

## Survivor Information

| CSV Column | Data Description |
| --- | --- |
| Person	| The survivor's name. |
| Class | The survivor's class.  One of 'Assault', 'Bruiser', 'Hunter', 'Scout', or 'Shooter'. |
| Hero | Whether or not this survivor is a hero or not.  'X' specifies a hero, anything else (or blank) is a normal survivor. |
| Lvl	| The survivor level. 1-32. |
| Stars	| The number of stars the survivor has.  This is expressed as a decimal.  The whole number portion denotes the stars the survivor has.  The decimal portion indicates how many traits have been leveled up toward the next star level. |
| Weapon | The weapon damage for the survivor.  Used to estimate the damage, critical damage, and charge damage. |
| Trait1 | The survivor's first (top) trait. |
| Trait2 | The survivor's second trait. |
| Trait3 | The survivor's third trait. |
| Trait4 | The survivor's fourth trait. |
| Trait5 | The survivor's last (bottom) trait. |
