import gamesets 

class Players:
    name_player = "null"
    ID = 0
    kills = None
    
    
    def __init__(self, name: str, ID: int): 
        self.name_player = name
        self.ID = ID
    
    #Changing the name, remains the same identification (ID) of the player.
    def change_info_user(self, 
                         identification: int, 
                         new_name: str, 
                         game: gamesets.Gamesets):
        pass
    
    def sum_kills(self, game: gamesets.Gamesets):
        self.kills = game.grouped.get(self.ID, None)
    
    
    
    
#     def get_kills(self):
#         return self.kills
    
#     def sending_info(self):
#         return self
        
        