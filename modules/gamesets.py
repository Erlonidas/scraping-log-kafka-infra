import re
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))   
sys.path.insert(0, current_dir) 
import killmethod 

class Gamesets:
    """
        Class created to resume information from the log. This class is divided in 2 method's \
        groups. The group 1 is where the scraping methods are, the second group is only for \
        getting and setting atributes of this class, mainly used for unittest. Check out a \
        quick summary of group 1:
    
        - Client Connect: Starting connection with the lobby.
        - User change info: Possibility of changing a player's name.
        - Client Begin: Players start interacting with other players in battlefield.
        - Kills: Collecting battle results.
        - Client disconnect: Checking if a player quits from the game, or gets disconnected.
        * Heat status: Data analysis about time to kill in game.
    """

    def __init__(self, ID: int, line: str):
        self.__ID_actual_game = 'game_'
        self.total_deaths = 0
        self.pre_lobby = [0,[1022, True, 'world']] # Before (3). {ID, clientBegin = True, 'name_player'}
        self.online = {1022: ['world',0]} # After (3). {ID: [name_player, total_kills]}
        self.disconnected = {} # Related to (5). Collection of kills from players data quit/disconnected the game.
        self.game_completed = True
        self.__mapname = None
        self.__gametype = None
        self.__ID_actual_game += str(ID) # EX: game_1
        try:
            self.__mapname = re.findall(r'\\mapname\\(.*?)\\', line)[0]
            self.__gametype = re.findall(r'\\g_gametype\\(\d+)\\', line)[0]
        except:
            pass
        
    
    def clientConnect(self, line: str):
        """
         Once detected a new player, attributes an ID while the player didn't set
         his name in game. For a while, an ID from a list is reserved for him.
         Since the first players is always ID = 2, the index 0 and 1 in the list is reserved.
         This list should have a maxlength according to lobby's settings.
         The lobby allows 16 players, so the list should contains at most length = 18
        """
        ID = re.findall(r":\s(\d+)", line)
        ID[0] = int(ID[0])
        ID.append(False)  # list: ID from user, False => not clientbegin yet.
        
        try: # In case someone quit the game, allows another one to get that ID
            self.pre_lobby[ID[0]] = ID
        except: # new player will always be added to this row.
            self.pre_lobby.append(ID)


    def userChangeInfo(self, line: str): 
        """
         Identifying who wants change name, or another player connected was allowed
         to uses ID from someone who disconnected.
        """
        user_new_name = re.findall(r'n\\(.*?)\\t', line)[0]
        ID_player = int(re.findall(r":\s(\d+) ", line)[0])
        
        # New name
        if  len(self.pre_lobby[ID_player]) == 2:
            self.pre_lobby[ID_player].append(user_new_name)
            
        # Updating a name    
        else:
            self.pre_lobby[ID_player][2] = user_new_name
            online = self.gets_online()
            valid_player = online.get(ID_player, 'no_player_found')
            if valid_player != 'no_player_found':
                online[ID_player][0] = user_new_name
                self.online = online


    def clientBegin(self, line: str):
        """
        Allow a new player to join with others, or checking if a player who got disconnected came back.
        """
        ID = re.findall(r":\s(\d+)", line)
        ID[0] = int(ID[0])
        index = ID[0]
        
        self.pre_lobby[index][1] = True 
        new_player_name = self.gets_Userinlobby(index)[2]
        disconnected = self.gets_disconnected()
        
        # Looks if a registered player disconnected came back.
        if new_player_name in disconnected:
            kills = self.disconnected.get(new_player_name)
            old_score = [new_player_name, kills]
            
            # Re-register but changing ID
            self.sets_online(index, old_score)
            
            #deleting from disconnected players.
            del self.disconnected[new_player_name]
        else:
            
            #[name_player, total_kills]
            self.sets_online(index,[new_player_name, 0]) 
        
        
    def kill(self,
             line: str, 
             kill_method: killmethod.Ways_of_killing):
        """
        Count kill points from each player. Register in kill_method class the weapon used.
        i) <world>'s point is counted for data analysis if the game doesnt wrap up correctly.
        ii) If a player be killed by <world> conditions, their score will be decreased.
        iii) If a player commit a suicide, nothing happens.
        """
        
        battle_result = re.findall(r'Kill: (\d+) (\d+) (\d+):', line)
        won = int(battle_result[0][0])
        killed = int(battle_result[0][1])
        weapon_ID = int(battle_result[0][2])
        
        if won == killed:
            return
        
        # total points in this game is incremented
        self.sets_newScore() 
        kill_method.add_kill_by_means(weapon_ID)
        score_board = self.gets_online()
        
        # If 'world' is the 'killer'  
        if won == 1022:  
            
            # update_score -> [name_player, kills]
            # update_score type -> list
            update_score = score_board.get(won) 
            update_score[1] += 1
            self.sets_online(won,  update_score)
            update_score = score_board.get(killed)
            update_score[1] -= 1
            self.sets_online(killed, update_score)
        else:
            
            # update_score = [name_player, kills]
            update_score = score_board.get(won) 
            update_score[1] += 1
            self.sets_online(won,  update_score)     

            
    def clientdisconnect(self, line: str):
        """
        If a players gives up, or disconnect from the game, 
        register the name, and number of kills.
        Then, make his old ID available for another player.
        """
        ID = re.findall(r":\s(\d+)", line)
        identification = int(ID[0])
        disconnected_player = self.gets_online().get(identification)
        name, kill = disconnected_player
        self.disconnected[name] = kill 
        
        # Cleaning data
        del self.online[identification]
        self.sets_Userinlobby(identification, [identification, False, None]) 
        
        
    def loadsObj_gameplay(self, kill_method: killmethod.Ways_of_killing):
        """
        Prepare all info to be sent to db controller
        """
        names = []
        online_dicts = self.gets_online().items()
        list_score = [chavelist for key, chavelist in online_dicts if key != 1022]
        for name, score in list_score:
            names.append(name)
            
        loudas = {
            f"{self.__ID_actual_game}": {
                "Total_kills": self.gets_boardResume(),
                "Players_online": names,
                "Players_disconnected: kills_each": self.gets_disconnected(),
                "Kills": dict(list_score),
                "Kill_by_means": kill_method.gets_board()
            }
        }
        return loudas
        
        
     # Methods below are used for getting and setting class attributes, primarily for unit testing

    def gets_gameID(self):
        # get info
        return self.__ID_actual_game
    
    
    def gets_boardResume(self):
        # get info
        return self.total_deaths
    
    def sets_boardResume(self, total: int):
        # get info
        self.total_deaths = total
    
    def sets_newScore(self):
        #SET info 
        self.total_deaths += 1
    
    
    def gets_Userinlobby(self, ID: int):
        # get info
        return self.pre_lobby[ID]
    
    
    def gets_listprelobby(self): 
        return self.pre_lobby
    
    
    def sets_Userinlobby(self, ID: int, new_one: list):
        # SET info
        length_prelobby = len(self.pre_lobby)
        if ID < length_prelobby:
            self.pre_lobby[ID] = new_one
        else:
            self.pre_lobby.append(new_one)
    
    
    def gets_online(self) -> dict:
        # get info
        return self.online
    
    
    def sets_online(self, ID: int, begin_lst: list):
        # SET info
        self.online[ID] = begin_lst
    
    
    def gets_disconnected(self):
        # get info
        return self.disconnected
    
    
    def sets_disconnected(self, name: str, kills: int):
        # get info
        self.disconnected[name] = kills
        

    def gets_initgame(self):
        return ((self.__mapname, self.__gametype))
    
    def replaceAll_on(self, package: dict):
        self.online = package
        
   
