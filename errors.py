class BaseGameException(Exception):
    peer_id = None
    
    def __init__(self, msg, peer_id=None):
        super().__init__(str(msg)+" in chat with peer_id "+str(peer_id))
        self.peer_id = peer_id

class GameOlreadyStarted(BaseGameException): pass
class GameNotStarted(BaseGameException): pass
class RecruitmentOlreadyStarted(BaseGameException): pass
class NotEnoughParticipants(BaseGameException): pass
