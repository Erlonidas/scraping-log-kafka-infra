import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))  
module_dir = os.path.abspath(os.path.join(current_dir, '../..', 'modules'))  
sys.path.insert(0, module_dir) 

from gamesets import Gamesets
from killmethod import Ways_of_killing

class Test_constructor:
    """    
    i) test_game_settings UC: Given a string to begin the game, collect the map and the type of it. 
    """
    
    def setup(self):
        self.stringLog = r"""
            0:00 InitGame: \sv_floodProtect\1\sv_maxPing\0\sv_minPing\0\sv_maxRate\10000\sv_minRate\0\sv_hostname\Code Miner Server\g_gametype\0\sv_privateClients\2\sv_maxclients\16\sv_allowDownload\0\dmflags\0\fraglimit\20\timelimit\15\g_maxGameClients\0\capturelimit\8\version\ioq3 1.36 linux-x86_64 Apr 12 2009\protocol\68\mapname\q3dm17\gamename\baseq3\g_needpass\0
        """
      
    def test_game_settings(self):
        game_id = 1
        gameset = Gamesets(game_id, self.stringLog)
        tuple_init = gameset.gets_initgame()
        assert tuple_init == ('q3dm17', '0')
         

class Test_clientConnect: # ClientConnect
    """
    test_clientConnect_new_ID UC: Check if a new player came
    """
    def test_clientConnect_new_ID(self):
        game_id = 1
        actual_game = Gamesets(game_id, '')
        line_in_log = "0:25 ClientConnect: 2" 
        actual_game.clientConnect(line_in_log)
        expected_prelobbyID = 2
        assert actual_game.gets_Userinlobby(expected_prelobbyID) == [2, False]


    def test_clientConnect_existing_ID(self):
        game_id = 10
        disconnected_player = [2, False, None] # length: 3
        line_in_log_1 = "0:25 ClientConnect: 2"
        line_in_log_2 = "5:34 ClientConnect: 2"
        actual_game = Gamesets(game_id, '')

        actual_game.clientConnect(line_in_log_1) # connecting
        actual_game.sets_Userinlobby(2, disconnected_player) # disconnecting
        actual_game.clientConnect(line_in_log_2)
        length_space = len(actual_game.gets_Userinlobby(2)) # len([2, False])
        assert length_space != len(disconnected_player) # 3 != 2 (ok)

        
class Test_userChangeinfo: 
    def setup(self):
        client_2 = "0:25 ClientConnect: 2"
        client_3 = "0:25 ClientConnect: 3"
        game_id = 5
        self.id_player = 3
        self.gameset = Gamesets(game_id, '')
        self.gameset.clientConnect(client_2)
        self.gameset.clientConnect(client_3)
        
    def test_add_new_name(self):
        line_in_log = r"1:01 ClientUserinfoChanged: 3 n\Isgalamido\t\0\model\uriel/zael\hmodel\..."
        self.gameset.userChangeInfo(line_in_log) 
        
        assert self.gameset.gets_Userinlobby(self.id_player) == [3, False, 'Isgalamido']

    def test_update_existing_name(self): 
        line_in_log = r"1:08 ClientUserinfoChanged: 3 n\Zeh\t\0\model\sarge/default\hmodel\..."
        player_prelobby = [self.id_player, True, 'Isgalamido']
        
        # Client begin ok: Isgalamido, 0 kills.
        player_online = {self.id_player: ['Isgalamido', 0]} # Client begin ok
        
        # Simulating a pre-existence of changed info at index 3.
        self.gameset.sets_Userinlobby(self.id_player, player_prelobby)  
        self.gameset.sets_online(self.id_player,
                            player_online.get(self.id_player))
        self.gameset.userChangeInfo(line_in_log) # Changing name
        
        # According from the string extracted from log, the new user is Zeh, in index 3.
        assert self.gameset.gets_Userinlobby(self.id_player) == [3, True, 'Zeh']
        
        # Check if it has changed in online players
        assert self.gameset.gets_online().get(self.id_player) == ['Zeh', 0]


class Test_clientBegin: # clientBegin method
    def setup(self):
        self.gameset = Gamesets(2, '')
        user = [2, False, 'generic_player']
        self.gameset.sets_Userinlobby(2, user)
        self.line_in_log = "1:01 ClientBegin: 2"
        self.player_id = 2
        self.player_KillScore = 0
         
    def test_newClientBegin(self):
        self.gameset.clientBegin(self.line_in_log)
        
        # Check if dict of players in game is keeping player already settup 
        assert self.gameset.gets_online().get(self.player_id) == ['generic_player', self.player_KillScore]
        
        boolean = self.gameset.gets_Userinlobby(self.player_id)[1]
        # Test changes boolean parameter at pre_lobby users from False 
        # to True.
        assert boolean == True

    def test_clientCameBack(self): 
        
        # Simulating player disconnected
        self.gameset.sets_disconnected('generic_player', 5) 
        self.gameset.clientBegin(self.line_in_log)
        
        #Client came back with old score = 5 instead of 0.
        assert self.gameset.gets_online().get(2) == ['generic_player', 5]
        

class Test_kill: # kill method
    def setup_method(self):
        self.mocinha = ['Mocinha', 0]
        self.isgalamido = ['Isgalamido', 0]
        self.gameset = Gamesets(1, '')
        self.kill_method = Ways_of_killing()
        self.gameset.sets_online(2, self.mocinha)
        self.gameset.sets_online(3, self.isgalamido)
        
    def teardown_method(self):
        del self.kill_method
        
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
        new_score = self.gameset.gets_online().get(2)[1]
        
        # Checking reduced point if world 'kills' someone
        assert new_score == loss_point
                                 
    def test_suicideWay(self):
        
        # Mocinha (2) killed Mocinha (2) using (22)-> MOD_TRIGGER_HURT 
        battle_result_1 = "0:00 Kill: 2 2 22: Mocinha killed Mocinha by MOD_TRIGGER_HURT"
        
        # before reading line log
        previous_ways_of_killing = self.kill_method.gets_board()
        previous_score = self.gameset.gets_online().get(2)[1]
        self.gameset.kill(battle_result_1, self.kill_method)
        
        # after reading line log
        final_ways_of_killing = self.kill_method.gets_board()
        final_score = self.gameset.gets_online().get(2)[1]
        
        # No diff from scoreboard
        assert  previous_score == final_score
        
        # kill_method keeps same state
        assert previous_ways_of_killing == final_ways_of_killing


class Test_clientDisconnection:
    def setup(self):
        zeh_prelobby = [2, True, 'zeh da manga']
        zeh_online = ['zeh da manga', 7]
        self.gameset = Gamesets(1, '')
        self.gameset.sets_Userinlobby(2, zeh_prelobby)
        self.gameset.sets_online(2, zeh_online)

    def test_clientdisconnect_successful(self):
        
        # Test the clientdisconnect method when a player disconnects successfully
        line_in_log = "13:05 ClientDisconnect: 2"
        ID_disconnected = 2
        self.gameset.clientdisconnect(line_in_log)
        infoBollean_prelobby = self.gameset.gets_Userinlobby(ID_disconnected)[1] 
        prelobby_name = self.gameset.gets_Userinlobby(ID_disconnected)[2] 
        info_online = self.gameset.gets_online() #dictionary
        
        # if dict is empty. User successfully deleted
        assert not info_online.get(ID_disconnected, False) 
        
        # Opening False for ID in pre_lobby...
        assert infoBollean_prelobby == False
        
        #assert info_prelobby[2][2] is None
        assert prelobby_name is None
        
        # Registering if score of user is registered for further analysis of game
        player, score = ('zeh da manga', 7)
        assert self.gameset.gets_disconnected() == {player: score}  
       
    
class Test_loadsObj_gameplay:
    
    @pytest.fixture
    def online_example(self):
        dic_group ={
            1022: ['world', 10],
            2: ['A', 2],
            3: ['B', 3],
            4: ['C', 4],
            8: ['D', 10]
        }
        return dic_group
    
    @pytest.fixture
    def kill_by_means_example(self):
        ways = {
            'MOD_GRENADE_SPLASH': 2,
            'MOD_MACHINEGUN': 6,
            'MOD_ROCKET_SPLASH': 6,
            'MOD_SHOTGUN': 5
        }
        return ways
    
    @pytest.fixture
    def Json_response(self):
        response = {
            'game_5': {
                "Total_kills": 19,
                "Players": ['A', 'B', 'C', 'D'],
                "Kills": {
                    'A': 2,
                    'B': 3,
                    'C': 4,
                    'D': 10
                },
                "Kill_by_means": {
                    'MOD_GRENADE_SPLASH': 2,
                    'MOD_MACHINEGUN': 6,
                    'MOD_ROCKET_SPLASH': 6,
                    'MOD_SHOTGUN': 5
                }
            }
        }
        return response
    
    @pytest.fixture                 
    def setup_method(self, kill_by_means_example, online_example):
        total_of_kills = 19
        self.gameset = Gamesets(5, '')
        self.kill_method = Ways_of_killing()
        self.gameset.replaceAll_on(online_example)
        self.kill_method.replaceAll_on(kill_by_means_example)
        self.gameset.sets_boardResume(total_of_kills)
        
    def test_sendingInfo(self, setup_method, Json_response):
        response = self.gameset.loadsObj_gameplay(self.kill_method)
        assert response == Json_response

        
if __name__ == '__main__':
    pytest.main()