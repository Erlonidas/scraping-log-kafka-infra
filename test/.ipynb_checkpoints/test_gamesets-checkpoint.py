import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))  
module_dir = os.path.abspath(os.path.join(current_dir, '..', 'modules'))  
sys.path.insert(0, module_dir) 

from gamesets import Gamesets
from killmethod import ways_of_killing

class Test_starts_connection(): # ClientConnect
    def test_clientConnect_new_ID(self):
        actual_game = Gamesets(1)
        line_in_log = "0:25 ClientConnect: 2" # Position in pre_lobby = 2
        actual_game.clientConnect(line_in_log)
        expected_prelobbyID = 2
        assert actual_game.gets_Userinlobby(expected_prelobbyID) == [2, False]


    def test_clientConnect_existing_ID(self):
        number_gameInlog = 10
        disconnected_player = [2, False, None]
        line_in_log_1 = "0:25 ClientConnect: 2"
        line_in_log_2 = "5:34 ClientConnect: 2"
        actual_game = Gamesets(number_gameInlog)

        actual_game.clientConnect(line_in_log_1)
        actual_game.sets_Userinlobby(2, disconnected_player)
        actual_game.clientConnect(line_in_log_2)
        length_space = len(actual_game.gets_Userinlobby(2))
        assert length_space != len(disconnected_player)

        
class Test_changing_user_info: # userChangeInfo method
    def test_add_new_name(self):
        new_connection = "0:25 ClientConnect: 3"
        line_in_log = r"1:01 ClientUserinfoChanged: 3 n\Isgalamido\t\0\model\uriel/zael\hmodel\..."
        
        gameset = Gamesets(1)
        gameset.clientConnect("0:01 ClientConnect: 2")
        gameset.clientConnect(new_connection)
        gameset.userChangeInfo(line_in_log) 
        
        # According from the string extracted from log, the new user is Isgalamido, in index 3.
        new_connection_index = 3
        assert gameset.gets_Userinlobby(new_connection_index) == [3, False, 'Isgalamido']

    def test_update_existing_name(self): 
        last_connection = "0:25 ClientConnect: 2"
        line_in_log = r"1:08 ClientUserinfoChanged: 3 n\Zeh\t\0\model\sarge/default\hmodel\..."
        player_prelobby = [3, True, 'old_name']
        player_online = {3: ['old_name', 0]}
        
        gameset = Gamesets(1)
        gameset.clientConnect(last_connection)
        
        # Simulating a pre-existence of changed info at index 3.
        gameset.sets_Userinlobby(3, player_prelobby)  
        gameset.sets_online(3, player_online.get(3))
        gameset.userChangeInfo(line_in_log) # Changing name
        
        # According from the string extracted from log, the new user is Zeh, in index 3.
        assert gameset.gets_Userinlobby(3) == [3, True, 'Zeh']
        
        # Check if it has changed in online players
        assert gameset.gets_online().get(3) == ['Zeh', 0]


class Test_user_becoming_player: # clientBegin method
    def setup(self):
        self.gameset = Gamesets(2)
        user = [2, False, 'generic_player']
        self.gameset.sets_Userinlobby(2, user)
        self.line_in_log = "1:01 ClientBegin: 2"
         
    def test_clientBegin(self):
        self.gameset.clientBegin(self.line_in_log)
        
        # Check of dict of players in game is keeping player already settup 
        assert self.gameset.gets_online().get(2) == ['generic_player', 0]
        
        # Test changes boolean parameter at pre_lobby users from false 
        # to True.
        assert self.gameset.gets_Userinlobby(2)[1] == True

    def test_clientCameBack(self): 
        # Simulating player disconnected
        self.gameset.sets_disconnected('generic_player', 5) 
        self.gameset.clientBegin(self.line_in_log)
        
        #Client came back with old score = 5 instead of 0.
        assert self.gameset.gets_online().get(2) == ['generic_player', 5]
    
    
class Test_scoreBoard: # kill method
    def setup_method(self):
        self.mocinha = ['Mocinha', 0]
        self.isgalamido = ['Isgalamido', 0]
        
        self.gameset = Gamesets(1)
        self.kill_method = ways_of_killing()
        self.gameset.sets_online(2, self.mocinha)
        self.gameset.sets_online(3, self.isgalamido)
        
    def test_kill_increment(self):
        # Ismagalido (3) killed Mocinha (2) using (6)-> MOD_ROCKET 
        battle_result = "1:08 Kill: 3 2 6: Isgalamido killed Mocinha by MOD_ROCKET"
           
        self.gameset.kill(battle_result, self.kill_method)
        
        # Game.gets_boardResume(): returns total deaths in game
        assert self.gameset.gets_boardResume() == 1
        
        # Confirming kill_by_means, attribute of kill_method, is well registered
        assert self.kill_method.gets_board().get('MOD_ROCKET') == 1
        
        # Testing if Isgalamido have score kill == 1
        assert self.gameset.gets_online().get(3) == ['Isgalamido', 1] 
    
    def test_world_penalty(self):
        # world (3) killed Mocinha (2) using (22)-> MOD_TRIGGER_HURT 
        battle_result_1 = "14:02 Kill: 1022 2 22: <world> killed Mocinha by MOD_TRIGGER_HURT"
        
        #pre-setting online player's score
        self.gameset.sets_online(2, ['Mocinha', 3])
        loss_point = 3 - 1 
        self.gameset.kill(battle_result_1, self.kill_method)
        
        # Checking reduced point if world 'kills' someone
        assert self.gameset.gets_online().get(2)[1] == loss_point
                                 
    
    def test_negative_score(self):
        # world (3) killed Mocinha (2) using (22)-> MOD_TRIGGER_HURT 
        battle_result_1 = "0:00 Kill: 1022 3 22: <world> killed Mocinha by MOD_TRIGGER_HURT"
        
        #pre-setting online player's score kill = 0
        self.gameset.sets_online(3, ['Isgalamido', 0])
        self.gameset.kill(battle_result_1, self.kill_method)
        
        # Not allowed negative score for Isgalamido
        final_score = 0
        assert self.gameset.gets_online().get(3)[1] == final_score


class Test_client_disconnection:
    def setup(self):
        zeh_prelobby = [2, True, 'zeh da manga']
        zeh_online = ['zeh da manga', 7]
        self.gameset = Gamesets(1)
        
        # Setting info that methods clientBegin and userchangeinfo should do.
        # including a few kills scored.
        self.gameset.sets_Userinlobby(2, zeh_prelobby)
        self.gameset.sets_online(2, zeh_online)

    def test_clientdisconnect_successful(self):
        # Test the clientdisconnect method when a player disconnects successfully
        line_in_log = "13:05 ClientDisconnect: 2"
        ID_disconnected = 2
        self.gameset.clientdisconnect(line_in_log)
        info_prelobby = self.gameset.gets_Userinlobby(ID_disconnected) #list length = 3
        info_online = self.gameset.gets_online() #dictionary
        
        # if dict is empty. User successfully deleted
        assert not info_online.get(ID_disconnected, False) 
        
        # Opening False for ID in pre_lobby...
        assert info_prelobby[1] == False
        
        # ... and old playes' name is None
        #assert info_prelobby[2][2] is None
        assert info_prelobby[2] is None
        
        # Registering if score of user is registered for further analysis of game
        assert self.gameset.gets_disconnected() == {'zeh da manga': 7}  
        

         
if __name__ == '__main__':
    pytest.main()