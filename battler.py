from math import floor
import math
from data import dataEnemies, dataItems
from objects import Item

import cmd, time
import random as rn

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

WPNHIT = 'weaponhit'
ATTACK = 'attack'
DEFENSE = 'defense'

ACTION_NORMAL = 0
ACTION_GUARDING = 1
ACTION_CHARGING = 2
ACTION_CHARGED = 3

class Battler:
    name = 'Empty Battler'
    hp = 0
    baseHp = 0
    level = 1
    exp = 0
    params = [0,0,0,0,0,0] #str,dex,con,int,cha,luk

    actionState = ACTION_NORMAL
    isAI = False

    def __init__(self): pass #constructor
    
    def __iter__(self):
        self.it = 0
        return self
    def __next__(self):
        if self.it < 6:
            self.it += 1
            x = None
            if self.it == 1: x = self.name
            elif self.it == 2: x = self.hpText()
            elif self.it == 3: x = self.level
            elif self.it == 4: x = self.exp
            elif self.it == 5: x = self.params
            elif self.it == 6: x = self.actionState
            return x
        else:
            raise StopIteration

    def getMaxHp(self):
        mhp = self.baseHp + (max(self.level-1, 0)) + 2*self.params[2]
        return mhp
    def getHp(self):
        return self.hp
    def setHp(self, value):
        self.hp = max(min(value, self.getMaxHp()), 0)
    def hpDamage(self, value):
        self.setHp(self.getHp() - value)
    def hpHeal(self, value):
        self.setHp(self.getHp() + value)
    def hpText(self):
        return "{0}/{1}".format(self.getHp(), self.getMaxHp())
    
    def gainExp(self, value):
        self.exp += value
        
    def gainGold(self, amount):
        self.gold += amount

    def isGuarding(self): return (self.actionState == ACTION_GUARDING)
    def isCharging(self): return (self.actionState == ACTION_CHARGING)
    def isCharged(self): return (self.actionState == ACTION_CHARGED)
    def setActionState(self, state):
        self.actionState = state
    def restoreActionState(self): # return 0 for normal action, 1 for forced attack
        if self.isGuarding():
            self.setActionState(ACTION_NORMAL)
            return 0
        elif self.isCharging():
            self.setActionState(ACTION_CHARGED)
            return 1
        elif self.isCharged():
            self.setActionState(ACTION_NORMAL)
            return 0
        return 0
    def chooseAction(self, target):
        return 1 #attack
    
    def getWpnHit(self): return 0
    def getAttack(self): return 0
    def getDefense(self): return 0

    def getLuckRoll(self):
        return rn.randint(0, min(0, self.params[5]))
    




class Enemy(Battler):
    isAI = True
    aiType = 0

    def __init__(self, name):
        self.name = name
        e = dataEnemies[name].copy()
        self.baseHp = e[HP]
        self.level = e[LEVEL] or 1
        self.exp = e[EXP]
        self.gold = e[GOLD]
        self.aiType = e[AI]
        self.params = e[BASEPARAMS]
        if "drops" in e:
            self.drops = e["drops"]
        else: self.drops = ["",""]

        # custom attack and defense values
        self.attack = e[ATTACK] #range
        self.defense = e[DEFENSE] #value
        self.isAI = True
        self.hpHeal(self.getMaxHp())
    
    def getAttack(self):
        return rn.choice(self.attack)
    def getDefense(self):
        return self.defense
    
    def chooseAction(self, target, turnCount):
        #0 is escape, 1 is attack, 2 is defend
        ret = 1
        if self.aiType == 0: #always attack
            ret = 1
        elif self.aiType == 1: #block every other turn
            if turnCount%2 == 0: ret = 2
            else: ret = 1

        return ret



#includes player and allies
class Actor(Battler):
    inventory = []
    weapon = None
    armor = None

    def __init__(self, name):
        self.name = name
        self.baseHp = 20
        self.exp = 0
        self.params = [1,1,1,1,1,1]
        self.isAI = False
        self.hpHeal(self.getMaxHp())
        self.gold = 10
    def fromArrays(self, stats, equips, inv):
        self.name = stats[0]
        self.hp = int(stats[1])
        self.baseHp = int(stats[2])
        self.level = int(stats[3])
        self.exp = int(stats[4])
        for i in range(6): self.params[i] = int(stats[i+5])
        self.gold = int(stats[11])

        if equips[0] != 'None': self.weapon = Item(equips[0])
        if equips[1] != 'None': self.armor = Item(equips[1])
        
        self.inventory = []
        for itemName in inv:
            if itemName != '': self.inventory.append(Item(itemName))
    def toString(self):
        s = self.name
        s += "|"+str(self.hp)+"|"+str(self.baseHp)+"|"+str(self.level)+"|"+str(self.exp)
        for i in range(6): s += "|"+str(self.params[i])
        s += "|"+str(self.gold)+"\n"
        
        if self.weapon: s += self.weapon.name + "|"
        else: s += "None|"
        if self.armor: s += self.armor.name + "|"
        else: s += "None"
        
        s += "\n"
        for item in self.inventory: s += item.name+"|"
        return s

    def getWpnHit(self):
        if isinstance(self.weapon, Item) and hasattr(self.weapon, 'hit'):
            return self.weapon.hit
        return 0
    def getAttack(self):
        if isinstance(self.weapon, Item):
            return rn.choice(getattr(self.weapon, 'attack', range(1,2)))
        return rn.choice(range(1,2)) #unarmed
    def getDefense(self):
        if isinstance(self.armor, Item):
            return self.armor.defense
        return 0 #unarmored  

    def getInventoryItemFromDesc(self, desc):
        itemList = list(set(self.inventory)) # make itemList unique
        for item in itemList:
            if desc in item.descWords:
                return item
        return None
    def getInventoryDescWords(self):
        itemList = list(set(self.inventory)) # make itemList unique
        descWords = []
        for item in itemList:
            descWords += item.descWords
        return descWords
    def getInventoryFirstDescWords(self):
        itemList = list(set(self.inventory)) # make itemList unique
        descWords = []
        for item in itemList:
            descWords.append(item.descWords[0])
        return descWords

    def expToLevelUp(self):
        # formula is 3 + floor( 0.02*(x^2) + 3x )
        x = self.level
        return math.floor(0.02*x*x + 3*x)
    def gainExp(self, value):
        super().gainExp(value)
        print("exptolevelup:",self.expToLevelUp())
        if self.level < 20: #20 is max level for now
            while (self.exp >= self.expToLevelUp()): self.levelUp()
    def levelUp(self):
        self.level += 1
        #gain two stats
        print("%s leveled up! You can increase any two stats by 1 point:" % self.name)
        
        statArray = ['str', 'dex', 'con', 'int', 'cha', 'luk']
        for r in range(2):
            while(True):
                string = "Choose one of "
                for j in range(6):
                    if statArray[j] != '': string += "[{}]".format(statArray[j].title())
                string += ": "
                inp = input(string).strip().lower()

                if statArray.count(inp) != 0:
                    self.params[statArray.index(inp)] += 1
                    statArray[statArray.index(inp)] = ''
                    break
                else: print("Try again...")


    #actions
    def showInventory(self):
        print('\nEquipment:')
        if self.weapon != None:
            print("  Weapon: %s" % self.weapon.name)
        else: print("  Weapon: (nothing)")
        if self.armor != None:   
            print("  Armor: %s" % self.armor.name)
        else: print("  Armor: (nothing)")

        if len(self.inventory) == 0:
            print('Inventory:\n  (nothing)')
            return
        else:
            # first get a count of each distinct item in the inventory
            itemCount = {}
            for item in self.inventory:
                if item.name in itemCount.keys():
                    itemCount[item.name] += 1
                else:
                    itemCount[item.name] = 1
            print('Inventory:')
            for item in set(self.inventory):
                if itemCount[item.name] > 1:
                    print("  x{} {}".format(itemCount[item.name], item))
                else:
                    print("  {}".format(item))

    def eat(self, item):
        if not isinstance(item, Item):
            print("ERROR: item is not Item object.")
            return
        if hasattr(item, 'heal'):
            print("You eat {0}, healing {1} HP.".format(item.shortDesc, item.heal))
            self.hpHeal(item.heal)
            self.inventory.remove(item)
            
        else: print("You can't consume that. Look for items with the (edible) tag.")

    def unequip(self, slot):
        if slot == 'weapon':
            if self.weapon == None:
                print("You already have no weapons equipped.")
            else:
                print('You unequip %s.' % (self.weapon.shortDesc))
                self.inventory.append(self.weapon)
                self.weapon = None
        elif slot == 'armor':
            if self.armor == None:
                print("You already have no armor equipped.")
            else:
                print('You unequip %s.' % (self.armor.shortDesc))
                self.inventory.append(self.armor)
                self.armor = None
        else: print("Unequip what? Type \"unequip weapon\" or \"unequip armor\" to strip that slot.")

    def equip(self, item):
        if not isinstance(item, Item):
            print("ERROR: item is not Item object.")
            return
        if hasattr(item, 'attack'):
            if self.weapon != None: self.unequip('weapon')
            print('You equip %s.' % (item.shortDesc))
            self.weapon = item
            self.inventory.remove(item)
        elif hasattr(item, 'defense'):
            if self.armor != None: self.unequip('armor')
            print('You equip %s.' % (item.shortDesc))
            self.armor = item
            self.inventory.remove(item)
        else:
            print("You can't equip that. Look for items with (weapon) or (armor) tags.")
    
    def use(self, item):
        if not isinstance(item, Item):
            print("ERROR: item is not Item object.")
            return
        if hasattr(item, 'heal'): self.eat(item)
        elif hasattr(item, 'attack') or hasattr(item, 'defense'): self.equip(item)
        #add more use cases here
        else: print("You can't use that item. Look for items with () tags.")






# manager
PHASE_TURN = 'turnphase'
PHASE_ACTOR = 'actorphase'
PHASE_ENEMY = 'enemyphase'
PHASE_ALLY = 'allyphase'

class BMExitException(Exception): pass
class BMNoBattlerException(Exception): pass
class BMDefeatException(Exception): pass
class BMEscapeException(Exception): pass
class BMVictoryException(Exception): pass

class BattleManagerCmd(cmd.Cmd):
    prompt = '\nbattle> '
    actor = None
    enemy = None

    turnCount = 0
    phase = PHASE_TURN

    def populate(self, battler1, battler2): # call this before starting a battle
        self.actor = battler1
        self.enemy = battler2
    def preloop(self): #start battle event
        if not isinstance(self.actor, Battler) or not isinstance(self.enemy, Battler):
            raise BMNoBattlerException
        
        print("Battle Started! {0} versus {1}!".format(self.actor.name, self.enemy.name))
        self.gameLoop()
    
    def end(self):
        raise BMExitException
    def victory(self):
        time.sleep(1)
        expGain = self.enemy.exp
        goldGain = self.enemy.gold
        expTotal = expGain + self.actor.exp
        print("{0} gained {1} EXP, for a total of {2} points.".format(self.actor.name, expGain, expTotal))
        self.actor.gainExp(expGain)
        print("{0} dropped {1} gold.".format(self.enemy.name, goldGain))
        self.actor.gainGold(goldGain)
        
        #one dropped item
        if hasattr(self.enemy, 'drops'):
            drop = rn.choice(self.enemy.drops)
            if drop != "": self.actor.inventory.append(Item(drop))
        
        time.sleep(2)
        
        raise BMVictoryException

    
    # to get player input, just return from gameloop
    def gameLoop(self):
        while(True):
            # print(self.phase)
            # print('current stack:',len(inspect.stack())) 
            # if self.turnCount > 300: self.end()
            if self.phase == PHASE_TURN:
                self.turnCount += 1
                time.sleep(1)
                print('\n\n===== TURN {} ====='.format(self.turnCount))
                print("{0}:   {1}/{2} HP".format(self.actor.name, self.actor.getHp(), self.actor.getMaxHp()))
                self.changePhase()
                continue

            elif self.phase == PHASE_ACTOR:
                time.sleep(1)
                self.actor.restoreActionState()
                print("actor action state: ",self.actor.actionState)
                if (not self.actor.isAI) and (self.actor.actionState == 0):
                    return
                else: #player input
                    self.processAIAction(self.actor)
                continue

            elif self.phase == PHASE_ENEMY:
                time.sleep(1)
                self.enemy.restoreActionState()
                print("enemy action state: ",self.enemy.actionState)
                self.processAIAction(self.enemy)
                continue

            elif self.phase == PHASE_ALLY:
                self.changePhase()
                continue

        
    def turnShift(self): pass
    def turnActor(self): pass
    def turnEnemy(self): pass
    def turnAlly(self): pass
        # if self.enemy.isAI:
        #     self.processAIAction()
        # else: return #player input
            #no allies yet

    def changePhase(self):
        if self.phase == PHASE_TURN: self.phase = PHASE_ACTOR
        elif self.phase == PHASE_ACTOR: self.phase = PHASE_ENEMY
        elif self.phase == PHASE_ENEMY: self.phase = PHASE_ALLY
        elif self.phase == PHASE_ALLY: self.phase = PHASE_TURN


    #AI equivalent of use cmd
    def processAIAction(self, user):
        if self.phase == PHASE_ACTOR:
            target = self.enemy
        elif self.phase == PHASE_ENEMY:
            target = self.actor
        
        if user.actionState == ACTION_CHARGED:
            self.actionAttack(user, target)
        else:
            action = user.chooseAction(target, self.turnCount)
            
            if action == 1:
                self.actionAttack(user, target)
            elif action == 2:
                self.actionCharge(user)
            elif action == 3:
                self.actionGuard(user)
            elif action == 4:
                self.actionHeal(user)
            elif action == 5:
                self.actionMagic(user, target)

        self.changePhase()
        self.gameLoop()

    def processPlayerAction(self, action):
        #test action states before this call
        if action == 0: #fleeing
            print("You try to run away...")
            if rn.randint(1,20) <= self.turnCount+self.actor.getLuckRoll():
                print("{} fled successfully!".format(self.actor.name))
                self.actor.actionState = 0
                raise BMEscapeException
            else:
                print("Couldn't escape!")
            #end of action
        elif action == 1:
            self.actionAttack(self.actor, self.enemy)
        elif action == 2:
            self.actionCharge(self.actor)
        elif action == 3:
            self.actionGuard(self.actor)
        elif action == 4:
            self.actionHeal(self.actor)
        elif action == 5:
            self.actionMagic(self.actor, self.enemy)

        #use current turn to deduce target
        #end of action
        self.changePhase()
        self.gameLoop()
        
    def actionAttack(self, attacker, defender):
        #hit formula 
        hitCheck =  150*( (attacker.params[1]+attacker.getWpnHit()) / (attacker.params[1]+defender.params[1])) - defender.getLuckRoll()
        hitRoll = rn.randint(1,100)
        print("Roll: {} on {}".format(hitRoll, hitCheck))
        if hitRoll > hitCheck:
            print("{}'s attack misses...".format(attacker.name))
        else:
            #damage formula
            atk = float(attacker.params[0])
            dfs = float(defender.getDefense())
            charge = 3 if (attacker.actionState == ACTION_CHARGED) else 1
            guard = 3 if (defender.actionState == ACTION_GUARDING) else 1
            dmg = math.floor( (atk + attacker.getAttack()*charge )*atk / (atk + dfs*guard) )
            #multipliers go here
            defender.hpDamage(dmg)
            print("{0} hits {1} for {2} points of damage!".format(attacker.name, defender.name, dmg))
            self.testForDefeat()
    def actionCharge(self, user):
        print("{} charges a strong attack...".format(self.actor.name))
        user.setActionState(ACTION_CHARGING) 
    def actionGuard(self, user):
        print("{} raises their guard against incoming attacks.".format(self.actor.name))
        user.setActionState(ACTION_GUARDING) 
    def actionHeal(self, user):
        heal = user.params[3] + rn.randint(1, user.params[3]) - 1
        user.hpHeal(heal)
        print("{0} casts a healing spell, recovering {1} HP.".format(user.name, heal))
    def actionMagic(self, user, target):
        print("{} casts a spell...".format(user.name))
        dmg = rn.randint(1, user.params[3])
        target.hpDamage(dmg)
        print("It hits {0}, dealing {1} points of damage!".format(target.name, dmg))
        self.testForDefeat()

    def testForDefeat(self):
        if self.actor.getHp() <= 0:
            print("{} was defeated.".format(self.actor.name))
            #actor ded
            raise BMDefeatException
        elif self.enemy.getHp() <= 0:
            print("{} was defeated!".format(self.enemy.name))
            self.actor.actionState = 0
            self.victory()

    #commands
    def default(self, arg):
        print('I do not understand that command. Type "help" for a list of commands.')
    def do_quit(self, arg):
        """Flees from the battle instantly."""
        return True # this exits the Cmd application loop in BattleManager.cmdloop()
    
    #def do_action(self, arg):
        #call processPlayerAction after any action
    #    self.processPlayerAction(1) #number for action chosen
    
    def do_flee(self, arg):
        """Attempt an escape (might not always succeed)."""
        self.processPlayerAction(0)
    #do_escape = do_flee
    def do_attack(self, arg):
        """Attack the enemy and attempt to deal damage."""
        self.processPlayerAction(1)
    def do_charge(self, arg):
        """Do a stronger attack that takes a turn to charge.\n(scales with weapon)"""
        self.processPlayerAction(2)
    def do_guard(self, arg):
        """Raise your defenses to reduce the damage taken next.\n(scales with armor)"""
        self.processPlayerAction(3)
    
    def do_heal(self, arg):
        """Conjure a healing spell on yourself."""
        self.processPlayerAction(4)
    #TODO: implement a spell list
    def do_cast(self, arg):
        """Conjure a damaging spell on the enemy."""
        self.processPlayerAction(5)
    


    def do_use(self, arg):
        """"use <item>": if item has () tags, do an action associated to that item."""
        name = arg.lower()
        if name == '':
            print('Use what? Type "inventory" to list your items.')
            return
        invDescWords = self.actor.getInventoryDescWords()
        if name not in invDescWords:
            print('You do not have "%s" in your inventory.' % (name))
            return
        item = self.actor.getInventoryItemFromDesc(name)
        self.actor.use(item)
    
    def do_status(self, arg):
        """Displays info on the current player, including HP, gold and level."""
        player = self.actor
        print("\nName: %s" % player.name)
        print("="*(len(player.name)+6))
        print("HP: {0}/{1} | {2} gold".format(player.getHp(), player.getMaxHp(), player.gold))
        print("Level {0} | {1} EXP".format(player.level, player.exp))
        print("\nStats:")
        st = player.params
        statsString = f"[{st[0]}]Str - [{st[1]}]Dex - [{st[2]}]Con\n[{st[3]}]Int - [{st[4]}]Cha - [{st[5]}]Luk"
        print(statsString)  
    def do_inventory(self, arg):
        """Display a list of the items in your possession."""
        self.actor.showInventory()
    do_inv = do_inventory 



    #return to gameloop
    # def postcmd(self, stop: bool, line: str) -> bool:
        
    #     self.phase = PHASE_ENEMY
    #     self.gameLoop()
    #     return super().postcmd(stop, line)

#external bm call
def createBattle(b1, b2):
    bm = BattleManagerCmd()
    bm.populate(b1, b2)
    try: 
        bm.cmdloop()
    except BMNoBattlerException:
        print("Error: Battle initialized without one or more battlers. Exiting...")
        return -1
    except BMExitException:
        return 1
    except BMVictoryException: #victory
        return 2
    except BMEscapeException: #escape
        return 1
    except BMDefeatException: #defeat
        return 0


# quick main
# pl = Actor("Jonas")
# en = Enemy("Slime")
# print(pl.exp)
# res = createBattle(pl, en)
# print(pl.exp)
