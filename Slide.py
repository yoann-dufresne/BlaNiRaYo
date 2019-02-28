from Photo import Photo

class Slide(object):
    """Slide"""
    def __init__(self, *photos):
        if len(photos) > 2 or len(photos) < 1:
            raise ValueError("Wrong number of photos")
        if len(photos) == 2:
            assert photos[0].orientation == photos[1].orientation == "V", "Both photos should be V"
            self.keywords = photo[0].keywords | photos[1].keywords
            self.id = photo[0].id + " " + photo[1].id
        if len(photos) == 1:
            assert photos[0].orientation == "H", "Photo should be H"
            self.keywords = photos[0].keywords
            self.id = photo[0].id

    def overlapp(self, photo):
        return len(self.keywords & photo.keywords), len(self.keywords - photo.keywords), len(photo.keywords - self.keywords)

    def score(self, photo):
        min(self.overlapp(photo))