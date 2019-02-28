import sys

class Solution():
    """docstring for Solution"""
    def __init__(self):
        self.slides = []

    def score(self):
        score = 0
        for idx in range(1,len(self.slides)):
            # print(idx, self.slides)
            score += self.slides[idx-1].score(self.slides[idx])

        return score

    def save(self):
        outfile_name = f"data/{sys.argv[1]}_{self.score()}.txt"
        print(f"saving {outfile_name}")
        outfile = open(outfile_name, "w")
        outfile.write(str(len(self.slides))+"\n")
        for slide in self.slides:
            outfile.write(f"{slide.id}\n")
        outfile.close()
        
