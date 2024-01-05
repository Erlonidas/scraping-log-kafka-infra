import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))  
module_dir = os.path.abspath(os.path.join(current_dir, '../..', 'modules'))  
sys.path.insert(0, module_dir)  

from analitics import HeatGame
from gamesets import Gamesets


@pytest.fixture(scope = 'class')
def myfix_analitics():
    log_init = r"\Code MinerServer\g_gametype\0\sv_priv...\protocol\68\mapname\q3dm17\gamename\..."
    gameset = Gamesets(1, log_init)
    analitics = HeatGame(gameset)
    return analitics
 

class Test_init:
    @pytest.mark.usefixtures("myfix_analitics")
    def test_constructor(self, myfix_analitics):
        assertion_expected = {
            'ID': 'Out_game_1',
            'gametype': '0',
            'mapname': 'q3dm17'
        }
        responseBody_analitics = myfix_analitics.get_attr()['info_init']()
        assert assertion_expected == responseBody_analitics


class Test_time_colected:
    def setup_method(self):
        self.linelog = " 20:54 Kill: 1022 2 22: <world> killed Isgalamido by MOD_TRIGGER_HURT" 
    
    @pytest.mark.usefixtures("myfix_analitics")
    def test_add_ratePoint(self, myfix_analitics):
        myfix_analitics.time_colected(self.linelog)
        
        # time_in_float 20min 54 sec == 20.9 min, in a list.
        time_in_float = [20.9] 
        assert myfix_analitics.get_attr()['list_ratePoint']() == time_in_float

class Test_Heat_in_Game:
    def setup(self):
        
        # kills in minutes
        self.list_of_kills = [
            12.4, 12.43, 14.03,
            14.25, 14.48, 14.63,
            14.77, 15.1, 15.3,
            15.45, 15.6, 15.63,
            15.9, 16.77
        ]
        
    @pytest.mark.usefixtures("myfix_analitics")
    def test_best_kill_rate(self, myfix_analitics):
        myfix_analitics.set_attr()['set_ratePoint'](self.list_of_kills)
        kill_by_minutes = myfix_analitics.kill_rate()
        expected_response = 5.0
        assert kill_by_minutes == expected_response
        
    def test_max_ttk(self, myfix_analitics):
        response_ttk = myfix_analitics.max_ttk()
        expected_ttk = 1.6
        assert response_ttk == expected_ttk

class Test_api_sendAll:
    
    @pytest.fixture
    def myfix_gameset(self):
        log_init = r"\Code MinerServer\g_gametype\0\sv_priv...\protocol\68\mapname\q3dm17\gamename\..."
        gameset = Gamesets(1, log_init)
        dict_group_online ={
            1022: ['world', 10],
            2: ['A', 2],
            3: ['B', 3],
            4: ['C', 4],
            8: ['D', 1]
        }
        
        dict_group_disconnected ={
            'E': 2,
            'F': 1, 
            'G': 1
        }
        gameset.online = dict_group_online
        gameset.disconnected = dict_group_disconnected
        return gameset
    
      
    def setup(self):
        self.list_of_kills = [
            12.4, 12.43, 14.03,
            14.25, 14.48, 14.63,
            14.77, 15.1, 15.3,
            15.45, 15.6, 15.63,
            15.9, 16.77
        ]

        self.response_expected = {
            'Out_game_1': {
                "Game map": 'q3dm17',
                "Game type": '0',
                "total_kills": 14,
                "Max players logged": 7,
                "ttk (min)": 1.6,
                "kill rate (min)": 5,
                "<World> score": 10
            }
        }

    @pytest.mark.usefixtures('myfix_analitics','myfix_gameset')     
    def test_max_players_logged(self, myfix_gameset, myfix_analitics):
        self.total = myfix_analitics.gets_MaxPlayers(myfix_gameset)
        total_players_expected = 7
        assert self.total == total_players_expected
    
    @pytest.mark.usefixtures('myfix_analitics','myfix_gameset')
    def test_send_loadedInfo(self, myfix_gameset, myfix_analitics):
        myfix_analitics.set_attr()['set_ratePoint'](self.list_of_kills)
        myResponse = myfix_analitics.loadsObj_analitcs(myfix_gameset)
        assert myResponse == self.response_expected
        
        
        

if __name__ == '__main__':
    pytest.main()