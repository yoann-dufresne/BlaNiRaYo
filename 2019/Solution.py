import sys
from Slide import Slide

class Solution():
    """docstring for Solution"""
    def __init__(self, photos=None, file=None):
        self.slides = []

        if file != None:
            sl = open(file).readlines()
            sl = sl[1:]
            for line in sl:
                if len(line.strip().split()) == 1:
                    x = int(line.strip())
                    self.slides += [Slide(photos[x])]
                else:
                    assert(len(line.strip().split()) == 2)
                    x,y = map(int,line.strip().split())
                    self.slides += [Slide(photos[x],photos[y])]
            print("evaluating",len(self.slides),"slides")
            print("score:",self.score())

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


        
