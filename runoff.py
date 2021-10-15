import io
import re
import csv
import sys
import argparse
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

    def drop_movies_with_no_first_votes(self,reorder):
        s = 0
        e = len(self.movies)
        while(s < e):
            if self.count_num_votes_for_movie(1,s) == 0:
                print(f'{self.movies[s]} dropped.')
                self.shift_first_votes(s)
                if reorder:
                    self.maxVote -= 1
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
    
    def reorder_ballots(self):
        for ballot in self.ballots:
            orderedVotes = sorted(ballot.votes)
            for i,v in enumerate(orderedVotes):
                idxToSwap = ballot.votes.index(v)
                ballot.votes[idxToSwap] = i + 1

    
    def runoff(self,slot,reorder):
        if slot == 1:
            self.ballots = [ballot for ballot in self.ballots if ballot.slot == 1]
        elif slot == 2:
            self.ballots = [ballot for ballot in self.ballots if ballot.slot == 2]
        self.print_movies()
        self.print_ballots()
        print('Dropping movies with no 1 votes')
        self.drop_movies_with_no_first_votes(reorder)
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
                    if reorder:
                        self.maxVote -= 1
                        self.reorder_ballots()
                    break
                else:
                    print(f'Tie for least {vote} votes; {", ".join([self.movies[idx] for idx in indicesToCheck])}')
                if vote == self.maxVote:
                    print(f'Full ballot tie; {", ".join([self.movies[idx] for idx in indicesToCheck])}')
                    randIndex = randint(0,len(indicesToCheck)-1)
                    print(f'{self.movies[randIndex]} has been randomly chosen to drop')
                    self.shift_first_votes(indicesToCheck[randIndex])
                    if reorder:
                        self.maxVote -= 1
                        self.reorder_ballots()
        print(f'\nWinner is: {self.movies[0]}')

def main():
    parser = argparse.ArgumentParser(description='Perform runoff vote calculations for movie night')
    parser.add_argument('-s','--slot',help='0 = all ballots, 1 = first slot only, 2 = second slot only',type=int, default=0)
    parser.add_argument('-r','--reorder_votes',help='after a movie is removed, reorder the ballot votes to the lowest possible numbers (i.e. [1,2,4,5,7] -> [1,2,3,4,5])',action='store_true')
    args = parser.parse_args()

    root = tk.Tk()
    root.withdraw()
    filepath = askopenfilename()
    slotPrint = "All" if args.slot == 0 else "First Slot" if args.slot == 1 else "Second Slot"
    print(f'\n~~~~~ Calculating Runoff for {slotPrint} Ballots ~~~~~')
    r = Runoff(filepath)
    r.runoff(args.slot,args.reorder_votes)
    print(f'~~~~~ Finished {slotPrint} Ballots ~~~~~')

def get_next_highest_in_array(start,arr):
    nextHighest = sys.maxsize
    for val in arr:
        if val < nextHighest and val > start:
            nextHighest = val
    return nextHighest

if __name__ == "__main__":
    main()