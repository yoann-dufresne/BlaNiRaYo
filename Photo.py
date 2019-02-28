
class Photo():
    """docstring for Photo"""
    def __init__(self, id, orientation, keywords):
        self.id = id
        self.orientation = orientation
        self.keywords = set(keywords)

    def overlapp(self, photo):
        return len(self.keywords & photo.keywords), len(self.keywords - photo.keywords), len(photo.keywords - self.keywords)

    def score(self, photo):
        min(self.overlapp(photo))