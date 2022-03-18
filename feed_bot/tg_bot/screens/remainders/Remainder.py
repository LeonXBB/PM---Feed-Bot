from ..Screen import Screen


class Remainder(Screen):
    
    remainders = []

    @classmethod
    def _get_(cls, name=None, id=None):
        
        for remainder in cls.remainders:
            if ((remainder.screen_id == id or id is None) and (remainder.screen_name == name or name is None)): 
                return remainder