class Ways_of_killing:
    def __init__(self):
        self.enum_lst = []
        self.kill_by_means = {}
        self.enum_lst = [
              'MOD_UNKNOWN',
              'MOD_SHOTGUN',
              'MOD_GAUNTLET',
              'MOD_MACHINEGUN',
              'MOD_GRENADE',
              'MOD_GRENADE_SPLASH',
              'MOD_ROCKET',
              'MOD_ROCKET_SPLASH',
              'MOD_PLASMA',
              'MOD_PLASMA_SPLASH',
              'MOD_RAILGUN',
              'MOD_LIGHTNING',
              'MOD_BFG',
              'MOD_BFG_SPLASH',
              'MOD_WATER',
              'MOD_SLIME',
              'MOD_LAVA',
              'MOD_CRUSH',
              'MOD_TELEFRAG',
              'MOD_FALLING',
              'MOD_SUICIDE',
              'MOD_TARGET_LASER',
              'MOD_TRIGGER_HURT',
            #ifdef MISSIONPACK
              'MOD_NAIL',
              'MOD_CHAINGUN',
              'MOD_PROXIMITY_MINE',
              'MOD_KAMIKAZE',
              'MOD_JUICED',
            #endif
              'MOD_GRAPPLE'
        ]
    

    def add_kill_by_means(self, identification: int):
        def die_method(death_from_log: int):
            if death_from_log < len(self.enum_lst):
                return self.enum_lst[death_from_log]
            else:
                return None
        
        means = die_method(identification)
        if not means == None:
            self.kill_by_means[means] = self.kill_by_means.get(means, 0) + 1
    
    def gets_board(self):
        return self.kill_by_means
    
    def replaceAll_on(self, package: dict):
        self.kill_by_means = package
    
        
        

        


        



        
        
    
    
    
    
    

