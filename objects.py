from data import dataItems

GROUNDDESC = 'grounddesc'
SHORTDESC = 'shortdesc'
LONGDESC = 'longdesc'
TAKEABLE = 'takeable'
EDIBLE = 'edible'
WPNHIT = 'weaponhit'
ATTACK = 'attack'
DEFENSE = 'defense'
DESCWORDS = 'descwords'


class Item:
    modified = False
    def __init__(self, name='Item Name'):
        i = dataItems[name].copy()
        self.name = name
        self.groundDesc = i[GROUNDDESC]
        self.shortDesc = i[SHORTDESC]
        self.longDesc = i[LONGDESC]
        self.isTakeable = i[TAKEABLE]
        
        #equipment
        if WPNHIT in i: self.hit = i[WPNHIT]
        if ATTACK in i: self.attack = i[ATTACK] #range
        if DEFENSE in i: self.defense = i[DEFENSE] #value
        if EDIBLE in i: self.heal = i[EDIBLE]

        self.descWords = i[DESCWORDS]
    
    def __repr__(self): # print in arrays and print()
        strWeapon  = ''
        strArmor = ''
        strEdible = ''
        if hasattr(self, 'attack'): strWeapon = '(weapon)'
        if hasattr(self, 'defense'): strArmor = '(armor)'
        if hasattr(self, 'heal'): strArmor = '(edible)'
        return "{} {}{}{}".format(self.name, strWeapon, strArmor, strEdible)
    
    # == operation
    def __eq__(self, other):
        if isinstance(other, Item):
            return ((self.name == other.name))
        else:
            return False
    
    # != operation
    def __ne__(self, other): 
        return (not self.__eq__(other))
    
    # for arrays
    def __hash__(self): 
        return hash(self.__repr__())