import json

'''CONSTANTS'''
#data parts
DESC = 'desc'
NORTH = 'north'
SOUTH = 'south'
EAST = 'east'
WEST = 'west'
UP = 'up'
DOWN = 'down'
GROUND = 'ground'
SHOP = 'shop'
ENEMIES = 'enemies'
GROUNDDESC = 'grounddesc'
SHORTDESC = 'shortdesc'
LONGDESC = 'longdesc'
TAKEABLE = 'takeable'
EDIBLE = 'edible'
WPNHIT = 'weaponhit'
ATTACK = 'attack'
DEFENSE = 'defense'
DESCWORDS = 'descwords'

HP = 'hitpoints'
EXP = 'experience'
GOLD = 'gold'
LEVEL = 'level'

BASEPARAMS = 'baseparams'
AI = 'aitype'
STR = 'strength'
DEX = 'dexterity'
CON = 'constitution'
INT = 'inteligence'
CHA = 'charisma'
LUK = 'luck'

WEAPON = 'weapon'
ARMOR = 'armor'


#stats
#hp
#str, dex, con, int, cha, luk
#weapon hit, armor

#formulas
#hit: roll + weapon hit + dex > 2*dex
#hp: base + level*con
#phy dmg: roll + str - armor
#mag dmg: roll + int
#heal: roll(int to 2*int)


'''DATA CONTAINERS'''

def loadRooms():
    with open('dataRooms.json') as json_file:
        dataRooms = json.load(json_file)
    return dataRooms

dataItems = {
    # map objects=========================
    'Welcome Sign': {
        GROUNDDESC: 'A welcome sign stands here.',
        SHORTDESC: 'a welcome sign',
        LONGDESC: 'The sign reads "Welcome to COMMAND LINE GAME (name pending)"',
        TAKEABLE: False,
        DESCWORDS: ['welcome sign', 'sign']
    },
    'Fountain': {
        GROUNDDESC: 'A bubbling fountain of green water.',
        SHORTDESC: 'a fountain',
        LONGDESC: 'The water in the fountain is a bright green color. Doesn\'t look right.',
        TAKEABLE: False,
        DESCWORDS: ['fountain']
    },

    # equipment===========================
    'Nice Sword':{
        GROUNDDESC: 'Someone left a nice sword laying around.',
        SHORTDESC: 'the nice, polished sword',
        LONGDESC: 'This sword hasn\'t seen a lot of action. You can imagine it cutting slimes like butter (a very strange, blue butter).',
        TAKEABLE: True,
        WPNHIT: 1, ATTACK: range(1,3),
        DESCWORDS: ['nice sword', 'sword']
    },
    'Iron Hammer':{
        GROUNDDESC: 'There\'s a cast iron hammer standing by the side.',
        SHORTDESC: 'the heavy hammer.',
        LONGDESC: 'This bad boy can hit hard, as long as you can hit anything at all.',
        TAKEABLE: True,
        WPNHIT: -1, ATTACK: range(3,5),
        DESCWORDS: ['iron hammer', 'hammer']
    },
    'Troll Club':{
        GROUNDDESC: 'An enormous wooden club was tossed on the ground previously.',
        SHORTDESC: 'the brutish wooden club.',
        LONGDESC: 'Some troll had to beat this piece of wood into this shape If it hasn\'t shattered in pieces until now, it won\'t break anytime soon.',
        TAKEABLE: True,
        WPNHIT: 1, ATTACK: range(2,7),
        DESCWORDS: ['troll club', 'club']
    },

    'Barrel Lid':{
        GROUNDDESC: 'A barrel lid, with no barrels in sight... maybe you could use it in some way?.',
        SHORTDESC: 'the improvised shield.',
        LONGDESC: 'It\'s not particularly strong, but you could theoretically block a sword with it.',
        TAKEABLE: True,
        DEFENSE: 1,
        DESCWORDS: ['barrel lid', 'lid']
    },

    # edible items========================
    'Donut': {
        GROUNDDESC: 'A fresh glazed donut is on the ground, what a waste...',
        SHORTDESC: 'the donut',
        LONGDESC: 'It\'s perfectly edible, even though it\'s not very nourishing.',
        TAKEABLE: True, # whether this item can be taken and put in your inventory
        EDIBLE: 3, 
        DESCWORDS: ['donut']
    },
    'Water Bottle': {
        GROUNDDESC: 'A fresh glazed donut is on the ground, what a waste...',
        SHORTDESC: 'the donut',
        LONGDESC: 'It\'s perfectly edible, even though it\'s not very nourishing.',
        TAKEABLE: True, # whether this item can be taken and put in your inventory
        EDIBLE: 2, 
        DESCWORDS: ['bottle', 'water bottle', 'water']
    },
    
    # drop items========================
    'Boar Tusks': {
        GROUNDDESC: 'A shiny pair of boar tusks, fresh from the source.',
        SHORTDESC: 'the pair of tusks',
        LONGDESC: 'Somewhat valuable, but who can you sell this to?.',
        TAKEABLE: True, # whether this item can be taken and put in your inventory
        EDIBLE: 3, 
        DESCWORDS: ['donut']
    },
    'Item Name': {
        GROUNDDESC: 'How this item is described when on the ground.',
        SHORTDESC: 'A short description of this item.',
        LONGDESC: 'A long description of this item, used when the player looks at it.',
        TAKEABLE: True, # whether this item can be taken and put in your inventory
        WPNHIT: 1, ATTACK: 0, DEFENSE: 0, # if atk > range(0,0) can be used as weapon, if def > 0 can be used as armor
        EDIBLE: 5, # how much this item heals when consumed
        DESCWORDS: ['a word the player can use to refer to this item', 'another word']
    }
}

dataEnemies = {
    'Slime': {
        HP: 5, LEVEL: 1, EXP: 1, GOLD: 1,
        BASEPARAMS: [1,1,1,1,1,1], AI: 0,
        ATTACK: range(0, 1), DEFENSE: 0
    },
    'Wolf': {
        HP: 6, LEVEL: 2, EXP: 3, GOLD: 3,
        BASEPARAMS: [2,2,1,1,1,1], AI: 0,
        ATTACK: range(0, 3), DEFENSE: 0
    },
    'Wasp': {
        HP: 4, LEVEL: 3, EXP: 5, GOLD: 7,
        BASEPARAMS: [2,5,1,1,1,1], AI: 0,
        ATTACK: range(2, 3), DEFENSE: 0
    },
    'Boar': {
        HP: 6, LEVEL: 4, EXP: 6, GOLD: 8,
        BASEPARAMS: [2,2,3,1,1,2], AI: 0, "drops": ["","Boar Tusks"],
        ATTACK: range(1, 5), DEFENSE: 2
    },
    'Goblin': {
        HP: 10, LEVEL: 4, EXP: 7, GOLD: 4,
        BASEPARAMS: [1,5,1,3,1,3], AI: 0,
        ATTACK: range(1, 3), DEFENSE: 1
    },
    'Blue Slime': {
        HP: 7, LEVEL: 5, EXP: 5, GOLD: 3,
        BASEPARAMS: [3,2,2,3,2,2], AI: 0,
        ATTACK: range(0, 1), DEFENSE: 1
    },
    'Troll': {
        HP: 8, LEVEL: 7, EXP: 5, GOLD: 3,
        BASEPARAMS: [6,2,4,3,1,2], AI: 0, "drops": ["","","Troll Club"],
        ATTACK: range(1, 6), DEFENSE: 3
    },
    'EnemyBase': {
        HP: 1, LEVEL: 1, EXP: 1, GOLD: 1,
        BASEPARAMS: [1,0,0,0,0,0], AI: 0,
        ATTACK: range(1, 3), DEFENSE: 0 #attack is range, defense is value
    },
}




