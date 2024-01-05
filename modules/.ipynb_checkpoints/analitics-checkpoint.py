import re
import os
import sys
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))   
sys.path.insert(0, current_dir)
import gamesets 

class HeatGame:
    """
        This class is designed to provide data analysis for GameSets objects. \
        Based on this class and the game's log, the 'heatGame' class was created as \
        a solution to gain insights into why players are not completing the game \
        until the very end. To address this issue, additional information will be \
        included for those incomplete games, such as:
            >> Game Map (info from object Gamesets)
            >> Game type = [DM, TDM, Tournament, CTF] (info from object Gamesets)
            >> Max players had began in game (info from object Gamesets)
            >> ttk = Max. time between two kills (exception for <world>)
            >> shutdown time = How long did the game last.
            >> kill rate = best kill/min.
            >> <world> score
    """
     
    def __init__(self, obj_: gamesets.Gamesets):
        self._ID_data_analysis = 'Out_'
        self._mapname = None
        self._gametype = None
        self.exit = 0
        self.shutdown = None
        self.ratePoint = []
        self.maxPlayers = 0
        self.ttk = 0

        #Initialize this class together with Gamesets' class
        mapInfo = obj_.gets_initgame()
        self._ID_data_analysis += obj_.gets_gameID()
        self._mapname = mapInfo[0]
        self._gametype = mapInfo[1]
        
    
    def time_colected(self, line: str):
        """
        Building a serie of float number, actually exactly time of kill.
        
        attr:
            line => string from log
        
        Returns:
            list: float time converted 
        """

        def time_to_float(line: str) -> float:

            """
            Convert time type into float. Used for data analysis.
            Every time that a kill occours, the line should be read by
            Gamesets' class and analitics' class.
            
            attr:
                line => string from log
            """
            response = re.findall(r'^\s*(\d{1,3}:\d{1,3})', line)
            battle_result = re.findall(r'Kill: (\d+) (\d+) (\d+):', line)
            won = int(battle_result[0][0])
            killed = int(battle_result[0][1])
            
            if won == killed:
                return None
            
            try:
                if len(response) != 0:
                    min_sec = response[0] 
                    min_sec = min_sec.replace(':','.').split('.')
                    min_sec = float(min_sec[0]) + float(min_sec[1])/60
                    return round(min_sec,2)
                else:
                    raise ValueError('ERROR: No time standarded was found.')
            except ValueError as e:
                print('Error in method time_colection.')
                return None
        
        if time_to_float(line) is not None:
            self.ratePoint.append(time_to_float(line))
        
    
    def kill_rate(self) -> float:
        """
        Getting interQuartil range, to compute best killrate of te game \
        accordig to data time colected from every kill in game, unless the \
        killer is <world>
    
        Returns:
            float: best kill rate (kill/min)
        """
        try:
            q1 = np.percentile(self.ratePoint, 25)
            q3 = np.percentile(self.ratePoint, 75)
            list4sum = [time for time in self.ratePoint if time >= q1 and time <= q3]

            if (q3-q1) == 0:
                return 'NaN'

            killrate = len(list4sum)/(q3-q1)
            return round(killrate, 0)
        except:
            return 'NaN'
    
    
    def gets_MaxPlayers(self, obj_gamesets: gamesets.Gamesets) -> int:
        
        # Maximum players that had connected to this game.
        # -1 because <world> is not considered as a player.
        self.maxPlayers = (len(obj_gamesets.gets_online())
                           + len(obj_gamesets.gets_disconnected())
                           -1)
        return self.maxPlayers
    
    
    def max_ttk(self):
        ttk = 0
        try:
            for index in range(len(self.ratePoint)-2):
                diff_time = self.ratePoint[index+1] - self.ratePoint[index]
                if diff_time > self.ttk:
                    self.ttk = diff_time 
            return round(self.ttk, 2)
        except:
            return 'NaN'
         
        
    def loadsObj_analitcs(self, obj_gamesets: gamesets.Gamesets) -> dict:
        loudas = {
            f"{self._ID_data_analysis}": {
                "Game map": self._mapname,
                "Game type":self._gametype,
                "total_kills": len(self.ratePoint),
                "Max players logged": self.gets_MaxPlayers(obj_gamesets),
                "ttk (min)": self.max_ttk(),
                "kill rate (min)": self.kill_rate(),
                "<World> score": obj_gamesets.gets_online()[1022][1]
            }
        }
        return loudas
    
    def get_attr(self):
        """
        Centralizing all methods that returns directly an attribute from instance class.
        Ex: response = instance.gets_attr()['some_attr_from_instance']()
        
        string 'some_attr_from_instance' => shoulb be replaced by nth:child() from get_attr
        """
        def list_ratePoint():
            return self.ratePoint
        
        def info_init():
            Response_game_analitics = {
            'ID': self._ID_data_analysis,
            'gametype': self._gametype,
            'mapname': self._mapname
        }
            return Response_game_analitics
        
        memo_attrReturns = {
            'list_ratePoint': list_ratePoint, 
            'info_init': info_init
        }
        return memo_attrReturns
    
    def set_attr(self):
        """
        Centralizing all methods that sets instances' attr
        """    
        def set_ratePoint(lista: list):
            self.ratePoint = lista
        
        memo_attrSetter = {
            'set_ratePoint': set_ratePoint
        }
        
        return memo_attrSetter
        
        
        
        
            
            
        

    
    
   
    
    
    