
class Photo():
    """docstring for Photo"""
    def __init__(self, id, orientation, keywords):
        self.id = id
        self.orientation = orientation
        self.keywords = set(keywords)

        
        