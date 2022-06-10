from os import name
import random
import data, battler
import cmd, textwrap, time

from objects import Item

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
ATTACK = 'attack'
DEFENSE = 'defense'
DESCWORDS = 'descwords'
#options
SCREEN_WIDTH = 80

'''GLOBALS'''
#options
showFullExits = True
#game vars
location = 'Town Square' # start in town square

player = battler.Actor("Player")
player.inventory = [Item('Water Bottle'),Item('Donut')] # start with blank inventory
#pointers
gold = player.gold
inventory = player.inventory 
worldRooms = data.loadRooms()
worldItems = data.dataItems


def displayLocation(loc):
    """A helper function for displaying an area's description and exits."""
    # Print the room name.
    print('\n\n' + loc)
    print('=' * len(loc))

    # Print the room's description (using textwrap.wrap())
    print('\n'.join(textwrap.wrap(worldRooms[loc][DESC], SCREEN_WIDTH)))

    # Print all the items on the ground.
    if len(worldRooms[loc][GROUND]) > 0:
        print()
        for item in worldRooms[loc][GROUND]:
            print(worldItems[item][GROUNDDESC])
    
    # Print if there are enemies in the area.
    if ENEMIES in worldRooms[loc]:
        if len(worldRooms[loc][ENEMIES]) > 5:
            print("The area is full of enemies.")
        elif len(worldRooms[loc][ENEMIES]) > 1:
            print("A couple of enemies roam the area.")
        elif len(worldRooms[loc][ENEMIES]) > 0:
            print("There's a single enemy here.")
        else:
            print("It appears the area is now clear of enemies.")
    print("\n")
    # Print all the exits.
    exits = []
    for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
        if direction in worldRooms[loc].keys():
            exits.append(direction.title())
    if showFullExits:
        for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
            if direction in worldRooms[location]:
                print('%s: %s' % (direction.title(), worldRooms[location][direction]))
    else:
        print('Exits: %s' % ' '.join(exits))
def moveDirection(direction):
    """A helper function that changes the location of the player."""
    global location
    if direction in worldRooms[location]:
        if worldRooms[location][direction] in worldRooms:
            print('You move to the %s.' % direction)
            location = worldRooms[location][direction]
            
            #respawn enemies
            populateEnemies()
            displayLocation(location)
        else:
            print('ERROR: That location does not exist. \n(if the name does not have WIP, send message to dev).')
    else:
        print('You cannot move in that direction')
def populateEnemies():
    for loc in worldRooms:
        if ENEMIES in worldRooms[loc]:
            if random.randint(0,1) == 0: #50% chance to populate
                worldEnms = worldRooms[loc][ENEMIES]
                spawnEnms = worldRooms[loc]['spawnlist']
                worldEnms.append(random.choice(spawnEnms))
                #print(worldEnms,"from", spawnEnms)
                if len(spawnEnms) < len(worldEnms):
                    worldEnms.remove(random.choice(worldEnms))



def saveGame(player, location):  
    with open("save/player.txt", "w") as file:
        file.write(player.toString())
        file.write("\n"+location)

'''STARTING INTERFACE'''
class SysCmd(cmd.Cmd):
    prompt = '\nsystem> '
    def default(self, arg):
        print('I do not understand that command. Type "help" for a list of commands.')
    def do_quit(self, arg):
        """Quit the game."""
        print('Thanks for playing!')
        return True
    
    #TODO: add an options menu

    def loadGame(self):
        stats = []
        equips = []
        inv = []
        global location
        global player
        with open("save/player.txt", 'r') as file:
            stats = file.readline().removesuffix("\n").split("|")
            equips = file.readline().removesuffix("\n").split("|")
            inv = file.readline().removesuffix("\n").split("|")
            location = file.readline()
        #print(stats)
        #print(equips)
        #print(inv)
        #print(location)
        player.fromArrays(stats, equips, inv)
    def do_load(self, arg):
        """Start the game from a .txt savefile."""
        self.loadGame()
        self.runGame()
    def do_new(self, arg):
        """Start the game with a new character."""
        while (True):
            global player
            player.name = input("Type the name of your character: ")
            print("%s, is that correct? [y][n]" % player.name)
            i = input()
            if i.strip().lower() == "y": break
        
        global location; location = 'Town Square' # start in town square

        self.runGame()
    do_new_game = do_new
    do_load_game = do_load
    
    def runGame(self):
        global worldRooms; worldRooms = data.loadRooms()
        
        print("   - start session!")
        time.sleep(1)
        displayLocation(location)
        TextAdventureCmd().cmdloop()
        print("   - end of session.")
        return True


def getAllDescWords(itemList):
    """Returns a list of "description words" for each item named in itemList."""
    itemList = list(set(itemList)) # make itemList unique
    descWords = []
    for item in itemList:
        descWords.extend(worldItems[item][DESCWORDS])
    return list(set(descWords))

def getAllFirstDescWords(itemList):
    """Returns a list of the first "description word" in the list of
    description words for each item named in itemList."""
    itemList = list(set(itemList)) # make itemList unique
    descWords = []
    for item in itemList:
        descWords.append(worldItems[item][DESCWORDS][0])
    return list(set(descWords))

def getFirstItemMatchingDesc(desc, itemList): #will be removed later
    itemList = list(set(itemList)) # make itemList unique
    for item in itemList:
        if desc in worldItems[item][DESCWORDS]:
            return item
    return None

def getAllItemsMatchingDesc(desc, itemList):
    itemList = list(set(itemList)) # make itemList unique
    matchingItems = []
    for item in itemList:
        if desc in worldItems[item][DESCWORDS]:
            matchingItems.append(item)
    return matchingItems

'''COMMAND INTERFACE'''
class TextAdventureCmd(cmd.Cmd):
    prompt = '\nworld> '
    # The default() method is called when none of the other do_*() command methods match.
    def default(self, arg):
        print('I do not understand that command. Type "help" for a list of commands.')

    # A very simple "quit" command to terminate the program:
    def do_quit(self, arg):
        """Quit the game."""
        return True # this exits the Cmd application loop in TextAdventureCmd.cmdloop()

    def help_a(self):
        print('aaaaaaa is not implemented in this program.')

    def do_save(self, arg):
        saveGame(player, location)
        print("Progress saved inside \"savefile.txt\".")

    # These direction commands have a long (i.e. north) and show (i.e. n) form.
    # Since the code is basically the same, I put it in the moveDirection()
    # function.
    def do_north(self, arg):
        """Go to the area to the north, if possible."""
        moveDirection('north')
        self.randomEncounter()

    def do_south(self, arg):
        """Go to the area to the south, if possible."""
        moveDirection('south')
        self.randomEncounter()

    def do_east(self, arg):
        """Go to the area to the east, if possible."""
        moveDirection('east')
        self.randomEncounter()

    def do_west(self, arg):
        """Go to the area to the west, if possible."""
        moveDirection('west')
        self.randomEncounter()

    def do_up(self, arg):
        """Go to the area upwards, if possible."""
        moveDirection('up')
        self.randomEncounter()

    def do_down(self, arg):
        """Go to the area downwards, if possible."""
        moveDirection('down')
        self.randomEncounter()

    def do_exits(self, arg):
        """Toggle showing full exit descriptions or brief exit descriptions."""
        global showFullExits
        showFullExits = not showFullExits
        if showFullExits:
            print('Showing full exit descriptions.')
        else:
            print('Showing brief exit descriptions.')

    def do_status(self, arg):
        """Displays info on the current player, including HP, gold and level."""

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
        player.showInventory()
    do_inv = do_inventory

    def do_take(self, arg):
        """"take <item> - Take an item on the ground."""

        # put this value in a more suitably named variable
        itemToTake = arg.lower()

        if itemToTake == '':
            print('Take what? Type "look" to see the items on the ground.')
            return

        cantTake = False

        # get the item name that the player's command describes
        for item in getAllItemsMatchingDesc(itemToTake, worldRooms[location][GROUND]):
            if worldItems[item].get(TAKEABLE, True) == False: #if you can't take the item
                cantTake = True
                continue # there may be other items named this that you can take, so we continue checking
            #else, you take the item
            print('You take %s.' % (worldItems[item][SHORTDESC]))
            worldRooms[location][GROUND].remove(item) # remove from the ground
            inventory.append(Item(item)) # add to inventory
            return

        if cantTake:
            print('You cannot take "%s".' % (itemToTake))
        else:
            print('That is not on the ground.')

    def do_drop(self, arg):
        """"drop <item> - Drop an item from your inventory onto the ground."""

        # put this value in a more suitably named variable
        itemToDrop = arg.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = player.getInventoryDescWords()

        # find out if the player doesn't have that item
        if itemToDrop not in invDescWords:
            print('You do not have "%s" in your inventory.' % (itemToDrop))
            return

        # get the item name that the player's command describes
        item = player.getInventoryItemFromDesc(itemToDrop)
        if item != None:
            print('You drop %s.' % (item.shortDesc))
            worldRooms[location][GROUND].append(item.name) # add to the ground
            inventory.remove(item) # remove from inventory

    def do_use(self, arg):
        """"use <item>": if item has () tags, do an action associated to that item."""
        name = arg.lower()
        if name == '':
            print('Use what? Type "inventory" to list your items.')
            return
        
        invDescWords = player.getInventoryDescWords()
        if name not in invDescWords:
            print('You do not have "%s" in your inventory.' % (name))
            return
        
        item = player.getInventoryItemFromDesc(name)
        player.use(item)

    def do_equip(self, arg):
        """"equip <item>": equip a weapon or armor in their respective slot."""
        itemToEquip = arg.lower()
        if itemToEquip == '':
            print('Equip what? Type "inventory" to list your items.')
            return
        
        invDescWords = player.getInventoryDescWords()
        if itemToEquip not in invDescWords:
            print('You do not have "%s" in your inventory.' % (itemToEquip))
            return
        
        item = player.getInventoryItemFromDesc(itemToEquip)
        player.equip(item)
        
    def do_unequip(self, arg):
        """"unequip weapon" or "unequip armor": removes item from that slot back to your inventory."""
        slot = arg.lower()
        player.unequip(slot)

    def complete_equip(self, text, line, begidx, endidx):
        text = text.lower()

        itemList = list(set(inventory)) # make itemList unique
        descWords = []
        for item in itemList:
            if hasattr(item, 'attack') or hasattr(item, 'defense'):
                descWords.append(item.descWords)
        
        if not text: #nothing typed in
            for item in itemList:
                if hasattr(item, 'attack') or hasattr(item, 'defense'):
                    descWords.append(item.descWords[0])

        #else, get starting letters
        invDescWords = player.getInventoryDescWords()
        descWords = []
        for desc in invDescWords:
            if desc.startswith(text): descWords.append(desc)
            print(descWords)
        return descWords

    def complete_take(self, text, line, begidx, endidx):
        possibleItems = []
        text = text.lower()

        # if the user has only typed "take" but no item name:
        if not text:
            return getAllFirstDescWords(worldRooms[location][GROUND])

        # otherwise, get a list of all "description words" for ground items matching the command text so far:
        for item in list(set(worldRooms[location][GROUND])):
            for descWord in worldItems[item][DESCWORDS]:
                if descWord.startswith(text) and worldItems[item].get(TAKEABLE, True):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique
    
    def complete_drop(self, text, line, begidx, endidx):
        itemToDrop = text.lower()
        possibleItems = []
        invDescWords = player.getInventoryDescWords()

        for descWord in invDescWords:
           if line.startswith('drop %s' % (descWord)):
                return [] # command is complete

        # if the user has only typed "drop" but no item name:
        if itemToDrop == '':
            return player.getInventoryFirstDescWords()

        # otherwise, get a list of all "description words" for inventory items matching the command text so far:
        for descWord in invDescWords:
            if descWord.startswith(text):
                possibleItems.append(descWord)
        return list(set(possibleItems)) # make list unique

    #fix inventory as well
    def do_look(self, arg):
        """Look at an item, direction, or the area:\n"look" - display the current area's description\n"look <direction>" - display the description of the area in that direction\n"look exits" - display the description of all adjacent areas\n"look <item>" - display the description of an item on the ground or in your inventory"""

        lookingAt = arg.lower()
        if lookingAt == '':
            # "look" will re-print the area description
            displayLocation(location)
            return

        if lookingAt == 'exits':
            for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
                if direction in worldRooms[location]:
                    print('%s: %s' % (direction.title(), worldRooms[location][direction]))
            return

        if lookingAt in ('north', 'west', 'east', 'south', 'up', 'down', 'n', 'w', 'e', 's', 'u', 'd'):
            if lookingAt.startswith('n') and NORTH in worldRooms[location]:
                print(worldRooms[location][NORTH])
            elif lookingAt.startswith('w') and WEST in worldRooms[location]:
                print(worldRooms[location][WEST])
            elif lookingAt.startswith('e') and EAST in worldRooms[location]:
                print(worldRooms[location][EAST])
            elif lookingAt.startswith('s') and SOUTH in worldRooms[location]:
                print(worldRooms[location][SOUTH])
            elif lookingAt.startswith('u') and UP in worldRooms[location]:
                print(worldRooms[location][UP])
            elif lookingAt.startswith('d') and DOWN in worldRooms[location]:
                print(worldRooms[location][DOWN])
            else:
                print('There is nothing in that direction.')
            return

        # see if the item being looked at is on the ground at this location
        item = getFirstItemMatchingDesc(lookingAt, worldRooms[location][GROUND])
        if item != None:
            print('\n'.join(textwrap.wrap(worldItems[item][LONGDESC], SCREEN_WIDTH)))
            return

        # see if the item being looked at is in the inventory
        item = getFirstItemMatchingDesc(lookingAt, inventory)
        if item != None:
            print('\n'.join(textwrap.wrap(worldItems[item][LONGDESC], SCREEN_WIDTH)))
            return

        print('You do not see that nearby.')

    def complete_look(self, text, line, begidx, endidx):
        possibleItems = []
        lookingAt = text.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = player.getInventoryDescWords()
        groundDescWords = getAllDescWords(worldRooms[location][GROUND])
        shopDescWords = getAllDescWords(worldRooms[location].get(SHOP, []))

        for descWord in invDescWords + groundDescWords + shopDescWords + [NORTH, SOUTH, EAST, WEST, UP, DOWN]:
            if line.startswith('look %s' % (descWord)):
                return [] # command is complete

        # if the user has only typed "look" but no item name, show all items on ground, shop and directions:
        if lookingAt == '':
            possibleItems.extend(getAllFirstDescWords(worldRooms[location][GROUND]))
            possibleItems.extend(getAllFirstDescWords(worldRooms[location].get(SHOP, [])))
            for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
                if direction in worldRooms[location]:
                    possibleItems.append(direction)
            return list(set(possibleItems)) # make list unique

        # otherwise, get a list of all "description words" for ground items matching the command text so far:
        for descWord in groundDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        # otherwise, get a list of all "description words" for items for sale at the shop (if this is one):
        for descWord in shopDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        # check for matching directions
        for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
            if direction.startswith(lookingAt):
                possibleItems.append(direction)

        # get a list of all "description words" for inventory items matching the command text so far:
        for descWord in invDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique

    def do_scout(self, arg):
        """Lists the enemies roaming the area."""
        if ENEMIES not in worldRooms[location]:
            print('There are no enemies here.')
            return
        
        print('You can scout:')
        for en in worldRooms[location][ENEMIES]:
            print(' - {}'.format(en))

    def gameOver(self):
        print("==== GAME OVER ====") 
        self.do_quit
    def do_battle(self, arg):
        """"battle <enemy>" - engage battle with an enemy in your current location"""
        if ENEMIES not in worldRooms[location]:
            print('There are no enemies here.')
            return
        if len(worldRooms[location][ENEMIES]) == 0:
            print('There are no enemies left, you should come back later.')
            #find some way to regenerate enemies (maybe on move event)
            return
        
        targetName = arg.title()    
        if targetName == '':
            print('Battle what? Type "enemy" or "enemies" to see the enemies in this location.')
            return
        
        if targetName not in worldRooms[location][ENEMIES]:
            print('There\'s no such enemy here. Type "enemy" or "enemies" to see the enemies in this location.')
        else:  #found enemy! engage in battle
            enemy = battler.Enemy(targetName)

            result = battler.createBattle(player, enemy)
            if result == 0: #game over
                self.gameOver()
                return True
            # elif result == 1:
            #     print("you're back into the map.")
            elif result == 2: #victory!
                worldRooms[location][ENEMIES].remove(targetName)
            
            displayLocation(location)

            return
    do_fight = do_battle

    def randomEncounter(self):
        global location
        if ENEMIES in worldRooms[location] and "random" in worldRooms[location]:
            chance = len(worldRooms[location][ENEMIES])
            if random.randint(1,5) <= chance:
                enemyName = random.choice(worldRooms[location][ENEMIES])
                print("A wild {} jumps at you!")
                self.do_battle(enemyName)

    #TODO: redo these
    def do_list(self, arg):
        """List the items for sale at the current location's shop. "list full" will show details of the items."""
        if SHOP not in worldRooms[location]:
            print('This is not a shop.')
            return

        arg = arg.lower()

        print('For sale:')
        for item in worldRooms[location][SHOP]:
            print('  - %s' % (item))
            if arg == 'full':
                print('\n'.join(textwrap.wrap(worldItems[item][LONGDESC], SCREEN_WIDTH)))

    def do_buy(self, arg):
        """"buy <item>" - buy an item at the current location's shop."""
        if SHOP not in worldRooms[location]:
            print('This is not a shop.')
            return

        itemToBuy = arg.lower()

        if itemToBuy == '':
            print('Buy what? Type "list" or "list full" to see a list of items for sale.')
            return

        item = getFirstItemMatchingDesc(itemToBuy, worldRooms[location][SHOP])
        if item != None:
            # NOTE - If you wanted to implement money, here is where you would add
            # code that checks if the player has enough, then deducts the price
            # from their money.
            print('You have purchased %s' % (worldItems[item][SHORTDESC]))
            inventory.append(item)
            return

        print('"%s" is not sold here. Type "list" or "list full" to see a list of items for sale.' % (itemToBuy))

    def complete_buy(self, text, line, begidx, endidx):
        if SHOP not in worldRooms[location]:
            return []

        itemToBuy = text.lower()
        possibleItems = []

        # if the user has only typed "buy" but no item name:
        if not itemToBuy:
            return getAllFirstDescWords(worldRooms[location][SHOP])

        # otherwise, get a list of all "description words" for shop items matching the command text so far:
        for item in list(set(worldRooms[location][SHOP])):
            for descWord in worldItems[item][DESCWORDS]:
                if descWord.startswith(text):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique

    def do_sell(self, arg):
        """"sell <item>" - sell an item at the current location's shop."""
        if SHOP not in worldRooms[location]:
            print('This is not a shop.')
            return

        itemToSell = arg.lower()

        if itemToSell == '':
            print('Sell what? Type "inventory" or "inv" to see your inventory.')
            return

        for item in inventory:
            if itemToSell in worldItems[item][DESCWORDS]:
                # NOTE - If you wanted to implement money, here is where you would add
                # code that gives the player money for selling the item.
                print('You have sold %s' % (worldItems[item][SHORTDESC]))
                inventory.remove(item)
                return

        print('You do not have "%s". Type "inventory" or "inv" to see your inventory.' % (itemToSell))

    def complete_sell(self, text, line, begidx, endidx):
        if SHOP not in worldRooms[location]:
            return []

        itemToSell = text.lower()
        possibleItems = []

        # if the user has only typed "sell" but no item name:
        if not itemToSell:
            return getAllFirstDescWords(inventory)

        # otherwise, get a list of all "description words" for inventory items matching the command text so far:
        for item in list(set(inventory)):
            for descWord in worldItems[item][DESCWORDS]:
                if descWord.startswith(text):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique

'''MAIN CODE'''
if __name__ == '__main__':
    print('Nate\'s Text Adventure RPG!')
    print('==========================')
    print('Type "new" to start a new session;')
    print('Type "help" to show all commands.')
    SysCmd().cmdloop()
