import io
import re
import csv
import sys
import tkinter as tk
from random import randint
from zipfile import ZipFile
from tkinter.filedialog import askopenfilename

class Ballot:
    def __init__(self, slot, votes):
        self.id = id
        self.slot = 1 if 'First' in slot else 2
        self.votes = votes

class Runoff:
    def __init__(self, filepath):
        self.lowest = 0
        self.movies = []
        self.ballots = []
        self.parseFile(filepath)
        self.maxVote = len(self.movies)
    
    def parseFile(self, filepath):
        zipcsv = ZipFile(filepath)
        zipname = zipcsv.namelist()[0]
        with io.StringIO(zipcsv.read(zipname).decode('utf-8')) as csvfile:
            reader = csv.reader(csvfile)
            self.movies = [re.search(r'\[(.+)\]', header).group(1) for header in reader.__next__()[1:-1]]
            for ballot in list(reader):
                self.ballots.append(Ballot(ballot[-1],[int(val) if val != '' else -1 for val in ballot[1:-1]]))
    
    def count_num_votes_for_movie(self,voteNum,movieIndex):
        return sum([1 for ballot in self.ballots if ballot.votes[movieIndex] == voteNum])

    def drop_movies_with_no_first_votes(self):
        s = 0
        e = len(self.movies)
        while(s < e):
            if self.count_num_votes_for_movie(1,s) == 0:
                print(f'{self.movies[s]} dropped.')
                self.shift_first_votes(s)
                e -= 1
            else:
                s += 1
    
    def shift_first_votes(self,movieIndex):
        for ballot in self.ballots:
            if ballot.votes[movieIndex] == 1:
                nextHighestVote = get_next_highest_in_array(1,ballot.votes)
                indToSwap = ballot.votes.index(nextHighestVote)
                ballot.votes[indToSwap] = 1
            ballot.votes.pop(movieIndex)
        self.movies.pop(movieIndex)
    
    def get_movie_indices_with_lowest_count_of_vote(self,indicesToCheck,voteNum):
        indexCounts = {idx:0 for idx in indicesToCheck}
        for ind in indicesToCheck:
            for ballot in self.ballots:
                if ballot.votes[ind] == voteNum:
                    indexCounts[ind] += 1
        lowest = min(indexCounts.values())
        return [key for key,val in indexCounts.items() if val == lowest]
    
    def print_movies(self):
        print([movie for movie in self.movies])
    
    def print_ballots(self):
        for ballot in self.ballots:
            print(ballot.votes)

    
    def runoff(self):
        self.print_movies()
        self.print_ballots()
        print('Dropping movies with no 1 votes')
        self.drop_movies_with_no_first_votes()
        while(len(self.movies) > 1):
            print()
            self.print_movies()
            self.print_ballots()
            indicesToCheck = list(range(len(self.movies)))
            for vote in range(1,self.maxVote+1):
                indicesToCheck = self.get_movie_indices_with_lowest_count_of_vote(indicesToCheck,vote)
                if len(indicesToCheck) == 1:
                    print(f'Dropping {self.movies[indicesToCheck[0]]}; least {vote} votes')
                    self.shift_first_votes(indicesToCheck[0])
                    break
                else:
                    print(f'Tie for least {vote} votes; {", ".join([self.movies[idx] for idx in indicesToCheck])}')
                if vote == self.maxVote:
                    print(f'Full ballot tie; {", ".join([self.movies[idx] for idx in indicesToCheck])}')
                    randIndex = randint(1,len(indicesToCheck))
                    print(f'{self.movies[randIndex]} has been randomly chosen to drop')
                    self.shift_first_votes(indicesToCheck[randIndex])
        print(f'\nWinner is: {self.movies[0]}')
    
    def runoff_first_slot(self):
        self.ballots = [ballot for ballot in self.ballots if ballot.slot == 1]
        self.runoff()
    
    def runoff_second_slot(self):
        self.ballots = [ballot for ballot in self.ballots if ballot.slot == 2]
        self.runoff()

def main():
    root = tk.Tk()
    root.withdraw()
    filepath = askopenfilename()
    print('\n~~~~~ Calculating Runoff for All Ballots ~~~~~')
    r = Runoff(filepath)
    r.runoff()
    print('~~~~~ Finished All Ballots ~~~~~')

    print('\n~~~~~ Calculating Runoff for First Slot Ballots ~~~~~')
    r1 = Runoff(filepath)
    r1.runoff_first_slot()
    print('~~~~~ Finished First Slot Ballots ~~~~~')

    print('\n~~~~~ Calculating Runoff for Second Slot Ballots ~~~~~')
    r2 = Runoff(filepath)
    r2.runoff_second_slot()
    print('~~~~~ Finished Second Slot Ballots ~~~~~')

def get_next_highest_in_array(start,arr):
    nextHighest = sys.maxsize
    for val in arr:
        if val < nextHighest and val > start:
            nextHighest = val
    return nextHighest

if __name__ == "__main__":
    main()