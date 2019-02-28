

class Solution():
    """docstring for Solution"""
    def __init__(self, arg):
        self.slides = []

    def score():
        score = 0
        for idx in range(1:len(self.slides)):
            score += self.slides[idx-1].score(self.slides[idx])

        return score

    def save(self):
        outfile = open(f"data/sol_{self.score()}.txt","w")
        f.write(str(len(self.slides))+"\n")
        for slide in self.slides:
            f.write(f"{slide.id}\n")
        f.close()
        
