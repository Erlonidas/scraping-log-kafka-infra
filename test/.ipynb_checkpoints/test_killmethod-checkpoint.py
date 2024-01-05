import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))  
module_dir = os.path.abspath(os.path.join(current_dir, '..', 'modules'))  
sys.path.insert(0, module_dir)  

from killmethod import ways_of_killing

class Test_matchesWeaponsUsed:
    def test_die_method_valid_death(self):
        ways = ways_of_killing()
        death = ways.die_method(5)
        assert death == 'MOD_GRENADE_SPLASH'

    def test_die_method_invalid_death(self):
        ways = ways_of_killing()
        death = ways.die_method(100)
        assert death is None

        
class Test_registerScore:   
    def test_add_kill_by_means(self):
        ways = ways_of_killing()
        ways.add_kill_by_means(1)  
        ways.add_kill_by_means(2)  
        ways.add_kill_by_means(1)  
        assert ways.gets_board() == {'MOD_SHOTGUN': 2, 'MOD_GAUNTLET': 1}
        
if __name__ == '__main__':
    pytest.main()