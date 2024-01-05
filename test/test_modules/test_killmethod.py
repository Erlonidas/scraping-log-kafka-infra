import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))  
module_dir = os.path.abspath(os.path.join(current_dir, '../..', 'modules'))  
sys.path.insert(0, module_dir)  

from killmethod import Ways_of_killing


class Test_add:
    
    def setup_method(self):
        self.myWays_instance = Ways_of_killing()
        self.myWays_instance.replaceAll_on({})
        
    def test_die_method_valid_death(self): 
        self.myWays_instance.add_kill_by_means(5)
        self.myWays_instance.add_kill_by_means(100)
        catalog_ways = self.myWays_instance.gets_board()
        assert catalog_ways == {'MOD_GRENADE_SPLASH': 1}
    
    def test_add_kill_updated(self):
        self.myWays_instance.add_kill_by_means(1)  
        self.myWays_instance.add_kill_by_means(2)  
        self.myWays_instance.add_kill_by_means(1)
        board = self.myWays_instance.gets_board()
        assert board == {'MOD_SHOTGUN': 2, 'MOD_GAUNTLET': 1}

        
class Test_replaceAll:
    @pytest.fixture
    def setsReplace(self):
        new_sets = {
            'MOD_GRENADE_SPLASH': 2,
            'MOD_ROCKET': 3,
            'MOD_ROCKET_SPLASH': 4,
            'MOD_PLASMA': 2,
            'MOD_PLASMA_SPLASH': 3
        }
        return new_sets
    
    def test_replaces_newset(self, setsReplace):
        setGroup_methods = setsReplace
        kill_method = Ways_of_killing()
        kill_method.replaceAll_on(setGroup_methods)
        assert kill_method.gets_board() == setGroup_methods
        
         
if __name__ == '__main__':
    pytest.main()