from Photo import Photo

class Slide(object):
    """Slide"""
    def __init__(self, *photos):
        if len(photos) > 2 or len(photos) < 1:
            raise ValueError("Wrong number of photos")
        if len(photos) == 2:
            assert photos[0].orientation == photos[1].orientation == "V", "Both photos should be V"
            self.keywords = photos[0].keywords | photos[1].keywords
            self.id = str(photos[0].id) + " " + str(photos[1].id)
            self.photos = (photos[0], photos[1])
        if len(photos) == 1:
            assert photos[0].orientation == "H", "Photo should be H"
            self.keywords = photos[0].keywords
            self.id = photos[0].id

    def overlapp(self, photo):
        return len(self.keywords & photo.keywords), len(self.keywords - photo.keywords), len(photo.keywords - self.keywords)

    def score(self, photo):
        return min(self.overlapp(photo))

    def switch_photos_A(self, slide):
        tmp = self.photos[0]
        self.photos = (slide.photos[0], self.photos[1])
        self.keywords = slide.photos[0].keywords | self.photos[1].keywords
        self.id = str(slide.photos[0].id) + " " + str(self.photos[1].id)

        slide.photos = (tmp, slide.photos[1])
        slide.keywords = tmp.keywords | slide.photos[1].keywords
        slide.id = str(tmp.id) + " " + str(slide.photos[1].id)

    def switch_photos_B(self, slide):
        tmp = self.photos[0]
        self.photos = (slide.photos[1], self.photos[1])
        self.keywords = slide.photos[1].keywords | self.photos[1].keywords
        self.id = str(slide.photos[1].id) + " " + str(self.photos[1].id)

        slide.photos = (slide.photos[0], tmp)
        slide.keywords = slide.photos[0].keywords | tmp.keywords
        slide.id = str(slide.photos[0].id) + " " + str(tmp.id)
