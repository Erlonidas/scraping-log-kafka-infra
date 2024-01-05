import killmethod

# Class created to resume informations from the log. All methods are based 
# on 5 main informations from Log. They are:
#     - (1) Client Connect. Starting connection with the lobby;
#     - (2) Client user change info. Possibility of changing player's name;
#     - (3) Client Begin. Player starts interacting with others players and battle field;
#     - (4) Kills. Colecting battles results
#     - (5) Client disconnect. Check possibility If a player quit from the game

class Gamesets:
    ID_actual_game = 'game_'
    total_deaths = 0
    pre_lobby = [0,[1022, True, 'world']] # Before (3). {ID, clientBegin = True, 'name_player'}
    online = {1022: ['world',0]} # After (3). {ID: [name_player, total_kills]}
    disconnected = {} # Related to (5). Collection of kills from players data quit/disconnected the game.
    
    def __init__(self, ID: int):  
        self.ID_game_number += str(ID) # EX: game_1
        
    
    def clientConnect(self, line: str):
        # Once detected a new player, attributes an ID while the player didn't set
        # his name in game. For a while, an ID from a list is reserved for him.
        # Since the first players is always ID = 2, the index 0 and 1 in the list is reserved.
        # This list should have a maxlength according to lobby's settings.
        # The lobby allows 16 players, so the list should contains length = 18
        
        ID = re.findall(r":\s(\d+)", line)
        ID[0] = int(ID[0])
        ID.append(False)  # list: ID from user, False => not clientbegin yet.
        
        try: # In case someone quit the game, allows another one to get that ID
            self.pre_lobby[ID[0]] = ID
        except:
            self.pre_lobby.append(ID)


    def userChangeInfo(self, line: str):
        # Identifying who wants change name, or a player that was allowed
        # to uses ID from someone who disconnected.
        user_new_name = re.findall(r'n\\(.*?)\\t', line)[0]
        ID_player = int(re.findall(r":\s(\d+) ", line)[0])
        
        if  len(self.pre_lobby[ID_player]) == 2:
            self.pre_lobby[ID_player].append(user_new_name)
        else:
            self.pre_lobby[ID_player][2] = user_new_name  


    def clientBegin(self, line: str):
        # Confirmed player to interact with others.
        ID = re.findall(r":\s(\d+)", line)
        ID[0] = int(ID[0])
        index = ID[0]
        self.pre_lobby[index][1] = True 
        self.online[index] =  [pre_lobby[index][2], 0] #[name_player, total_kills]

    def kill(self, line: str, kill_method: killmethod.ways_of_killing):
        #####
        self.total_deaths += 1
        
        battle_result = re.findall(r'Kill: (\d+) (\d+) (\d+):', line) # return list len = 1 of tuple of 3
        won = int(battle_result[0][0])
        #killed = int(battle_result[0][1])
        weapon_ID = int(battle_result[0][2])
        
        self.online[won][1] += 1 
        kill_method.add_kill_by_means(weapon_ID)
        pass

    def clientdisconnect(self, identification: int):
        # If a players gives up, or disconnect from the game, register the name, and number of kills.
        # Then, make his old ID available for another player.
        
        name = self.online.get(identification)[0]
        self.disconnected[name] = self.online.get(identification)[1] # {name_player_quit: total_kills}
        del self.online[identification]
        self.pre_lobby[identification][1] = False # Turn the ID available for new player.
        self.pre_lobby[identification[2] = None # Delete name from the list 
        
        
    
 