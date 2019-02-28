
class Photo():
    """docstring for Photo"""
    def __init__(self, id, orientation, keywords):
        self.id = id
        self.orientation = orientation
        self.keywords = set(keywords)

    def overlapp(self, photo):
        return len(tags1 & tags2), len(tags1 - tags2), len(tags2 - tags1)

    def score(self, photo):
        min(self.overlapp(photo))